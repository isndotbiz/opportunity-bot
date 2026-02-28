---
status: pending
priority: p1
issue_id: "003"
tags: [code-review, python, resource-leak, llm-cache, daemon]
dependencies: []
---

# llm_cache.py _get_cache_conn() leaks SQLite connections in long-running daemon

## Problem Statement

The proposed `_get_cache_conn()` function returns a raw `sqlite3.Connection`. Using it with `with _get_cache_conn() as conn:` manages the *transaction* (commit/rollback) but does NOT close the connection. In a long-running systemd daemon processing 150 opportunities/day, each `get_cached_analysis()` and `cache_analysis()` call opens a new connection that is never closed. This leaks file descriptors until the OS limit is reached.

## Findings

- `sqlite3.Connection.__exit__` commits or rolls back the transaction — it does NOT call `conn.close()`
- 2 FDs opened per analyzed opportunity (one read, one write)
- At 150 opportunities/day: ~300 FDs/day leaked; default Linux FD limit is 1024 → service crashes after ~3 days
- Plan is inconsistent: `get_pgvector_connection()` correctly calls `conn.close()` in `finally:`; `_get_cache_conn()` does not
- Additionally: SQLite default journal mode (DELETE) means concurrent ProcessPoolExecutor writers receive `database is locked` error
- Review source: Kieran Python Reviewer (P1-2); Performance Oracle (P3-D, P1-A)

## Proposed Solutions

### Option 1: Convert to @contextmanager (consistent with get_pgvector_connection)

**Approach:**
```python
from contextlib import contextmanager

@contextmanager
def _get_cache_conn():
    conn = sqlite3.connect(CACHE_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS llm_cache (
        url_hash TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        analysis_json TEXT NOT NULL,
        cached_at TEXT NOT NULL
    )""")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

**Pros:**
- Fixes both connection leak and WAL mode issues
- Consistent with `get_pgvector_connection()` pattern
- WAL mode allows concurrent readers + 1 writer (needed for 4-worker ProcessPoolExecutor)

**Cons:**
- Changes every call site from `with _get_cache_conn() as conn:` (no syntax change needed)

**Effort:** 30 minutes

**Risk:** Low

---

### Option 2: Module-level persistent connection

**Approach:** Hold one SQLite connection for the lifetime of the process, initialized at module load.

**Pros:**
- Eliminates per-call `connect()` overhead
- Natural fit for single-threaded pipeline script

**Cons:**
- Not safe for ProcessPoolExecutor workers (each process needs own connection)
- Harder to test in isolation

**Effort:** 1 hour

**Risk:** Medium

---

## Recommended Action

To be filled during triage.

## Technical Details

**Affected files:**
- `llm_cache.py` (new file per plan) — `_get_cache_conn()` function

**Related components:**
- `production_opportunity_pipeline.py` — calls `get_cached_analysis()` and `cache_analysis()`
- systemd service — long-running process where FD leaks accumulate

## Resources

- **Plan:** lines 514-547 (llm_cache.py spec)
- **Review source:** Kieran Python Reviewer (P1-2); Performance Oracle (P1-A, P3-D)

## Acceptance Criteria

- [ ] `_get_cache_conn()` is a `@contextmanager` that calls `conn.close()` in `finally:`
- [ ] WAL mode enabled: `PRAGMA journal_mode=WAL`
- [ ] `timeout=30` set to handle concurrent writer contention
- [ ] 1000 sequential calls to `get_cached_analysis()` produce no FD growth (verify with `lsof -p <pid>`)
- [ ] Concurrent writes from 2+ processes do not raise `OperationalError: database is locked`

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)

**Actions:**
- Traced sqlite3.Connection.__exit__ semantics — confirmed it does NOT close()
- Calculated FD leak rate: 300/day at current scrape volume
- Identified WAL mode need for ProcessPoolExecutor scenario
- Confirmed inconsistency with get_pgvector_connection() pattern
