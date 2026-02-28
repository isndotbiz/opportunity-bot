---
status: pending
priority: p1
issue_id: "005"
tags: [code-review, python, llm-cache, concurrency, performance]
dependencies: ["003"]
---

# SQLite LLM cache missing WAL mode — concurrent ProcessPoolExecutor writers silently fail

## Problem Statement

The proposed `llm_cache.py` uses SQLite with the default DELETE journal mode. The plan also proposes 4 parallel ProcessPoolExecutor workers for LLM analysis. These two combine to produce `sqlite3.OperationalError: database is locked` when two workers attempt to write cached results simultaneously. The plan's `except Exception: return` pattern means these errors are silently swallowed — the cache write is lost and the opportunity is re-analyzed on the next run, defeating the purpose of the cache.

## Findings

- SQLite default journal mode: DELETE — only one writer at a time, readers block during writes
- ProcessPoolExecutor with 4 workers: concurrent writes guaranteed when multiple analyses complete near-simultaneously
- `_get_cache_conn()` has no `timeout` parameter — default is `5` seconds, but lock contention spikes can exceed this
- Silent failure: exception is caught and ignored in caller
- WAL mode allows concurrent readers + 1 writer without blocking; suitable for this workload
- Review source: Performance Oracle (P1-A)

## Proposed Solutions

### Option 1: Enable WAL mode with timeout (resolves todo 003 simultaneously)

**Approach:**
```python
conn = sqlite3.connect(CACHE_PATH, timeout=30)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")  # safe with WAL; ~2x faster than FULL
```

**Pros:**
- WAL allows concurrent readers + 1 writer — eliminates lock contention for the 4-worker scenario
- `timeout=30` provides 30s wait before raising `OperationalError`
- `synchronous=NORMAL` is safe with WAL and reduces write latency

**Cons:**
- Creates a `-wal` and `-shm` sidecar file alongside the SQLite database
- Must be cleaned up if database is deleted

**Effort:** 15 minutes (same fix as todo 003)

**Risk:** Low

---

### Option 2: Single-writer cache with queue

**Approach:** Dedicate one process to cache writes; workers send results via `multiprocessing.Queue`.

**Pros:**
- Eliminates lock contention entirely
- Cache writes are serialized and never fail

**Cons:**
- Adds significant complexity (queue, dedicated process, shutdown coordination)
- Overkill for a SQLite cache with 4 writers

**Effort:** 4+ hours

**Risk:** Medium

---

## Recommended Action

To be filled during triage. Option 1 is preferred and combines with todo 003.

## Technical Details

**Affected files:**
- `llm_cache.py` (new file per plan) — `_get_cache_conn()`

## Resources

- **Review source:** Performance Oracle (P1-A)
- **SQLite WAL docs:** https://www.sqlite.org/wal.html

## Acceptance Criteria

- [ ] `PRAGMA journal_mode=WAL` set on every connection
- [ ] `timeout=30` set to handle write contention
- [ ] 4 concurrent processes calling `cache_analysis()` simultaneously do not raise `OperationalError`
- [ ] Cache correctly stores results from all 4 workers

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
