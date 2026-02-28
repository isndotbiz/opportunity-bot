#!/usr/bin/env python3
"""
LLM Analysis Result Cache — SQLite-backed, WAL mode, multi-process safe.

Design decisions:
- One connection per operation (not a persistent shared connection): correct for
  ProcessPoolExecutor where each worker is a separate OS process. SQLite's WAL
  file-level locking handles cross-process serialization; no Python lock needed.
- WAL journal mode: set once at DB creation, persists across all future connections.
- PRAGMA synchronous = NORMAL: safe with WAL for a cache (not financial data).
  A transaction may roll back after a power loss, but the DB will never corrupt.
- PRAGMA busy_timeout = 30000 ms: workers wait up to 30 s before raising
  OperationalError when another process holds the write lock.
- Exponential backoff retry: thin wrapper over busy_timeout for OperationalError
  cases that slip through (e.g. SQLITE_BUSY_SNAPSHOT in WAL mode).
- Key: uuid5(NAMESPACE_URL, url) as TEXT PRIMARY KEY — deterministic, collision-free.
- Value: JSON-serialized analysis result stored as TEXT.

Usage:
    from llm_cache import get_cached_result, cache_result, init_cache_db

    init_cache_db()   # call once at daemon startup

    result = get_cached_result(url)
    if result is None:
        result = call_llm(url)
        cache_result(url, result)
"""

import json
import logging
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DEFAULT_DB_PATH = Path(__file__).parent / "data" / "llm_cache.db"

# How long (seconds) sqlite3.connect() waits before raising OperationalError.
# This is the Python-level knob; PRAGMA busy_timeout (ms) is the SQLite knob.
# Both are set; they work together. The PRAGMA takes precedence once connected.
_CONNECT_TIMEOUT_SECONDS: float = 30.0

# PRAGMA busy_timeout in milliseconds — must be >= _CONNECT_TIMEOUT_SECONDS * 1000
# to avoid the connect() timeout firing before SQLite's internal retry loop.
_BUSY_TIMEOUT_MS: int = 30_000

# Retry settings for OperationalError "database is locked" that escape busy_timeout.
# This happens in WAL mode under SQLITE_BUSY_SNAPSHOT (reader-writer conflict at
# the WAL snapshot boundary). Three retries with exponential backoff is sufficient
# for 4 workers.
_MAX_RETRIES: int = 3
_RETRY_INITIAL_DELAY: float = 0.1  # seconds; doubles each attempt


# ---------------------------------------------------------------------------
# Pragma block — which settings persist, which must be set per connection
# ---------------------------------------------------------------------------
#
# PERSIST across connections (written into the DB file header):
#   - PRAGMA journal_mode = WAL    ← set once at init, never needs repeating
#   - PRAGMA auto_vacuum           ← set once at creation
#
# MUST be set on every new connection (connection-local, not stored in file):
#   - PRAGMA busy_timeout          ← milliseconds; replaces sqlite3 timeout arg
#   - PRAGMA synchronous           ← defaults to FULL; set to NORMAL for perf
#   - PRAGMA cache_size            ← defaults to ~2 MB; tune if needed
#   - PRAGMA temp_store            ← defaults to file; set to MEMORY for speed
#   - PRAGMA mmap_size             ← 0 by default; enable for read-heavy loads
#
# See: https://sqlite.org/pragma.html


# ---------------------------------------------------------------------------
# Core context manager
# ---------------------------------------------------------------------------

@contextmanager
def _sqlite_connection(
    db_path: Path = _DEFAULT_DB_PATH,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Open a SQLite connection with production-safe PRAGMAs, yield it inside an
    explicit transaction, commit on clean exit, roll back on any exception, and
    always close the connection.

    This is the ONLY place connections are created in this module. Every call
    opens a fresh connection — correct for ProcessPoolExecutor workers (separate
    OS processes), where connection objects cannot be pickled or shared.

    Isolation level is set to None (autocommit off is Python default, but we
    manage transactions manually with explicit BEGIN/COMMIT/ROLLBACK for clarity).
    """
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(
            str(db_path),
            timeout=_CONNECT_TIMEOUT_SECONDS,  # Python-level wait before connect raises
            check_same_thread=False,            # safe: one connection per process/call
            isolation_level=None,               # disable Python's implicit transaction mgmt
                                                # we issue BEGIN/COMMIT/ROLLBACK ourselves
        )
        conn.row_factory = sqlite3.Row

        # --- Per-connection PRAGMAs (must be set on every new connection) ---

        # SQLite will wait up to 30 s before returning SQLITE_BUSY.
        # Measured in milliseconds. Overrides the connect(timeout=) for SQL ops.
        conn.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")

        # NORMAL: safe with WAL. DB never corrupts; a committed txn may roll back
        # after an OS crash (acceptable for a cache — worst case is a cache miss).
        # Much faster than FULL (no fsync per commit, only at WAL checkpoint).
        conn.execute("PRAGMA synchronous = NORMAL")

        # Keep temporary tables/indices in RAM instead of temp files.
        conn.execute("PRAGMA temp_store = MEMORY")

        # 32 MB page cache per connection. Negative value = KiB units.
        conn.execute("PRAGMA cache_size = -32000")

        # Memory-mapped I/O up to 128 MB — reduces syscall overhead on reads.
        conn.execute("PRAGMA mmap_size = 134217728")

        # Begin an explicit transaction. WAL mode allows concurrent readers here.
        conn.execute("BEGIN")

        yield conn

        # Success path: commit.
        conn.execute("COMMIT")

    except sqlite3.OperationalError:
        # Roll back before re-raising so no partial write escapes.
        if conn is not None:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass  # connection may already be unusable; ignore secondary error
        raise

    except Exception:
        if conn is not None:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
        raise

    finally:
        if conn is not None:
            conn.close()


# ---------------------------------------------------------------------------
# Retry wrapper
# ---------------------------------------------------------------------------

def _with_retry(func, *args, **kwargs):
    """
    Call func(*args, **kwargs) up to _MAX_RETRIES times, sleeping with
    exponential backoff between attempts when an OperationalError containing
    "locked" is raised.

    busy_timeout handles most contention internally in the C layer. This Python
    retry layer catches the residual SQLITE_BUSY_SNAPSHOT errors that WAL mode
    can emit when a writer has advanced the WAL past a reader's snapshot.
    """
    delay = _RETRY_INITIAL_DELAY
    last_exc: Optional[Exception] = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except sqlite3.OperationalError as exc:
            last_exc = exc
            if "locked" in str(exc).lower():
                if attempt < _MAX_RETRIES:
                    logger.warning(
                        "SQLite locked (attempt %d/%d), retrying in %.2f s: %s",
                        attempt, _MAX_RETRIES, delay, exc,
                    )
                    time.sleep(delay)
                    delay *= 2  # exponential backoff
                else:
                    logger.error(
                        "SQLite locked after %d attempts, giving up: %s",
                        _MAX_RETRIES, exc,
                    )
                    raise
            else:
                raise  # non-lock OperationalError — re-raise immediately

    raise last_exc  # should be unreachable


# ---------------------------------------------------------------------------
# One-time database initialisation
# ---------------------------------------------------------------------------

def init_cache_db(db_path: Path = _DEFAULT_DB_PATH) -> None:
    """
    Create the cache database and schema if they do not exist.

    Call once at daemon startup (before spawning ProcessPoolExecutor workers).
    This is the ONLY place journal_mode=WAL is set. Because WAL mode persists
    in the database file header, workers that open the file later inherit it
    automatically — no worker needs to know about WAL at all.

    Thread/process safety: safe to call from multiple processes simultaneously
    because CREATE TABLE IF NOT EXISTS is idempotent and SQLite's file locking
    prevents simultaneous schema writes.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Use a plain connection here (not the context manager) because we need to
    # issue journal_mode BEFORE the first transaction begins — some SQLite
    # builds require this. journal_mode must be executed outside a transaction.
    conn = sqlite3.connect(str(db_path), timeout=_CONNECT_TIMEOUT_SECONDS)
    try:
        conn.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")

        # Set WAL mode. This is PERSISTENT — written into the DB file.
        # All future connections (including from worker processes) inherit it.
        # Safe to call repeatedly; SQLite returns the current mode as a result.
        result = conn.execute("PRAGMA journal_mode = WAL").fetchone()
        if result and result[0] != "wal":
            logger.warning("journal_mode is '%s', expected 'wal'", result[0])

        conn.execute("PRAGMA synchronous = NORMAL")

        # Enable incremental auto-vacuum so the file shrinks over time without
        # a full VACUUM. Set at creation; cannot be changed after DB has data.
        conn.execute("PRAGMA auto_vacuum = INCREMENTAL")

        # Schema — idempotent.
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS llm_cache (
                cache_key   TEXT PRIMARY KEY,   -- uuid5(NAMESPACE_URL, url)
                url         TEXT NOT NULL,       -- original URL for debugging
                result_json TEXT NOT NULL,       -- JSON-serialized LLM output
                created_at  TEXT NOT NULL        -- ISO-8601 timestamp
                    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                hit_count   INTEGER NOT NULL DEFAULT 0,
                last_hit_at TEXT                 -- ISO-8601 timestamp of last read
            );

            CREATE INDEX IF NOT EXISTS idx_llm_cache_url
                ON llm_cache (url);

            CREATE INDEX IF NOT EXISTS idx_llm_cache_created
                ON llm_cache (created_at);
        """)

        conn.commit()
        logger.info("LLM cache DB initialised: %s", db_path)

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Cache key
# ---------------------------------------------------------------------------

def _make_cache_key(url: str) -> str:
    """Return a deterministic uuid5 string key for a URL."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_cached_result(
    url: str,
    db_path: Path = _DEFAULT_DB_PATH,
) -> Optional[Any]:
    """
    Look up a cached LLM result by URL.

    Returns the deserialized Python object on a cache hit, or None on a miss.
    Updates hit_count and last_hit_at in the same transaction.

    Called from the main pipeline process before dispatching to the LLM.
    """
    key = _make_cache_key(url)

    def _get():
        with _sqlite_connection(db_path) as conn:
            row = conn.execute(
                "SELECT result_json FROM llm_cache WHERE cache_key = ?",
                (key,),
            ).fetchone()

            if row is None:
                return None

            # Update hit statistics (best-effort; failure here is not critical).
            conn.execute(
                """
                UPDATE llm_cache
                SET hit_count   = hit_count + 1,
                    last_hit_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
                WHERE cache_key = ?
                """,
                (key,),
            )

            return json.loads(row["result_json"])

    return _with_retry(_get)


def cache_result(
    url: str,
    result: Any,
    db_path: Path = _DEFAULT_DB_PATH,
) -> None:
    """
    Store an LLM analysis result for a URL.

    Uses INSERT OR REPLACE so that re-analysing a URL updates the cached value
    rather than raising an IntegrityError. Safe to call from multiple
    ProcessPoolExecutor workers simultaneously — WAL serializes writers at the
    OS file-locking layer; busy_timeout makes workers wait rather than fail.

    Args:
        url:    The source URL that was analysed.
        result: Any JSON-serializable Python object (dict, list, str, etc.).
        db_path: Path to the SQLite database file.
    """
    key = _make_cache_key(url)
    result_json = json.dumps(result, ensure_ascii=False)

    def _set():
        with _sqlite_connection(db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO llm_cache
                    (cache_key, url, result_json, created_at, hit_count, last_hit_at)
                VALUES
                    (?, ?, ?, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), 0, NULL)
                """,
                (key, url, result_json),
            )

    _with_retry(_set)
    logger.debug("Cached result for: %s (key=%s)", url, key)


def delete_cached_result(
    url: str,
    db_path: Path = _DEFAULT_DB_PATH,
) -> bool:
    """
    Remove a cached result by URL. Returns True if a row was deleted.
    Useful when re-running analysis on a URL that has stale data.
    """
    key = _make_cache_key(url)

    def _delete():
        with _sqlite_connection(db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM llm_cache WHERE cache_key = ?", (key,)
            )
            return cursor.rowcount > 0

    return _with_retry(_delete)


def cache_stats(db_path: Path = _DEFAULT_DB_PATH) -> dict:
    """
    Return cache statistics for monitoring/logging.

    Example output:
        {
            "total_entries": 1543,
            "total_hits": 87234,
            "oldest_entry": "2026-01-15T08:00:00Z",
            "newest_entry": "2026-02-26T12:34:56Z",
            "db_size_bytes": 4194304,
        }
    """
    def _stats():
        with _sqlite_connection(db_path) as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*)          AS total_entries,
                    SUM(hit_count)    AS total_hits,
                    MIN(created_at)   AS oldest_entry,
                    MAX(created_at)   AS newest_entry
                FROM llm_cache
            """).fetchone()
            return {
                "total_entries": row["total_entries"] or 0,
                "total_hits":    row["total_hits"] or 0,
                "oldest_entry":  row["oldest_entry"],
                "newest_entry":  row["newest_entry"],
                "db_size_bytes": db_path.stat().st_size if db_path.exists() else 0,
            }

    return _with_retry(_stats)


def run_maintenance(db_path: Path = _DEFAULT_DB_PATH) -> None:
    """
    Perform routine maintenance: WAL checkpoint and incremental vacuum.

    Schedule periodically (e.g. once per day via systemd timer or at daemon
    startup). The WAL file can grow unboundedly without checkpointing; this
    keeps it compact. incremental_vacuum reclaims deleted pages without a
    full file rewrite.

    Do NOT call this from worker processes — call from the main process only
    when no concurrent writes are expected (e.g., at startup or shutdown).
    """
    conn = sqlite3.connect(str(db_path), timeout=_CONNECT_TIMEOUT_SECONDS)
    try:
        conn.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")
        # Checkpoint: flush WAL into the main DB file, then reset WAL to zero.
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        # Reclaim freed pages (requires auto_vacuum = INCREMENTAL).
        conn.execute("PRAGMA incremental_vacuum")
        conn.commit()
        logger.info("LLM cache maintenance complete: %s", db_path)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Module-level convenience: allow `python llm_cache.py` for quick inspection
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_DB_PATH
    print(f"Cache DB: {db_path}")

    init_cache_db(db_path)
    stats = cache_stats(db_path)
    print(f"Entries : {stats['total_entries']:,}")
    print(f"Hits    : {stats['total_hits']:,}")
    print(f"Oldest  : {stats['oldest_entry']}")
    print(f"Newest  : {stats['newest_entry']}")
    print(f"DB size : {stats['db_size_bytes'] / 1024:.1f} KB")
