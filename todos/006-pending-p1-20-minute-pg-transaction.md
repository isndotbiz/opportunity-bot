---
status: pending
priority: p1
issue_id: "006"
tags: [code-review, database, postgresql, transactions, pipeline]
dependencies: []
---

# Single psycopg2 connection wraps entire 15-20 minute pipeline run — single PG transaction

## Problem Statement

The plan proposes `with get_pgvector_connection() as conn:` wrapping the entire pipeline run. The context manager commits on `__exit__`, meaning all 150 INSERTs are in one long-running transaction. Any exception mid-pipeline rolls back all work. PostgreSQL holds row locks for the entire duration, blocking autovacuum and creating a 15-20 minute transaction that negates the idempotency of the `ON CONFLICT DO UPDATE` design.

## Findings

- Plan step 1.2: "Open connection with `with get_pgvector_connection() as conn:` wrapping the entire pipeline run"
- psycopg2 default: autocommit=False → all operations in one implicit transaction until `conn.commit()`
- `get_pgvector_connection()` calls `conn.commit()` in `__exit__` → one commit for the full run
- Any unhandled exception → full rollback of all 150+ processed opportunities
- PostgreSQL autovacuum blocked for entire 15-20 minute window
- `ON CONFLICT DO UPDATE` idempotency is only useful if rows are committed per-batch, not per-run
- Review source: Performance Oracle (P1-B)

## Proposed Solutions

### Option 1: Commit in batches of 50 records

**Approach:**
```python
COMMIT_BATCH_SIZE = 50
batch = []
for opp in analyzed_opportunities:
    batch.append(prepare_for_insert(opp))
    if len(batch) >= COMMIT_BATCH_SIZE:
        with get_pgvector_connection() as conn:
            execute_values(conn.cursor(), INSERT_SQL, batch)
        batch.clear()
if batch:
    with get_pgvector_connection() as conn:
        execute_values(conn.cursor(), INSERT_SQL, batch)
```

**Pros:**
- Each batch committed independently — partial pipeline runs save work
- Autovacuum can run between batches
- Connection open time: milliseconds per batch instead of 20 minutes

**Cons:**
- Opens multiple connections (mitigated by connection pool in todo 026)
- Slightly more code

**Effort:** 1 hour

**Risk:** Low

---

### Option 2: One connection, explicit per-batch commits

**Approach:** Open one connection at pipeline start, call `conn.commit()` after each batch explicitly.

**Pros:**
- One TCP connection for the full run (no connection overhead)

**Cons:**
- Does not use the context manager pattern — requires explicit `try/except/finally`
- Inconsistent with the `get_pgvector_connection()` pattern in the plan

**Effort:** 1-2 hours

**Risk:** Medium (manual transaction management)

---

## Recommended Action

To be filled during triage.

## Technical Details

**Affected files:**
- `production_opportunity_pipeline.py` — proposed INSERT loop (plan step 1.2)
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — update step 1.2

## Resources

- **Review source:** Performance Oracle (P1-B)

## Acceptance Criteria

- [ ] No single transaction lasts more than 2 minutes
- [ ] Partial pipeline run (killed mid-way) saves already-processed records
- [ ] Autovacuum is not blocked for the full pipeline duration
- [ ] ON CONFLICT idempotency works correctly with batched commits

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
