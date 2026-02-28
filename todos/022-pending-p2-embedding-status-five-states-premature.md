---
status: pending
priority: p2
issue_id: "022"
tags: [code-review, database, schema, yagni, premature-optimization]
dependencies: []
---

# embedding_status 5-state enum is premature — use WHERE embedding IS NULL instead

## Problem Statement

The plan adds `embedding_status TEXT NOT NULL DEFAULT 'pending' CHECK (IN ('pending','processing','complete','failed','skipped'))`. This solves a distributed-worker embedding pipeline problem that week-1 doesn't have. The plan's own approach stores embeddings immediately at INSERT time (batch before INSERT). "processing" and "pending" states require a background worker that doesn't exist. The NULL check on `embedding` column is sufficient and already supported by the HNSW partial index.

## Findings

- Plan approach: "batch all embeddings before INSERT" — there is no asynchronous embedding step
- "processing" state: requires atomic state transitions to be safe — implies a background worker that doesn't exist
- "skipped" state: no logic shown that sets this value
- "pending" state: every row starts here but immediately becomes "complete" if the batch approach is followed
- The HNSW partial index already handles `WHERE embedding IS NOT NULL` — no status column needed for similarity search
- ON CONFLICT UPDATE SET must reset `embedding_status = 'pending'` (see todo 004) — adds complexity
- Review source: Code Simplicity Reviewer (P2-S7)

## Proposed Solutions

### Option 1: Replace with embedding IS NULL check

**Approach:** Remove `embedding_status` column. Track embedding completeness via:
```sql
WHERE embedding IS NULL   -- needs embedding
WHERE embedding IS NOT NULL  -- has embedding (HNSW partial index covers this)
```

**Pros:**
- Removes a column, a partial index, a CHECK constraint
- No need to write `embedding_status = 'complete'` on every successful INSERT
- Simpler ON CONFLICT clause

**Cons:**
- Cannot distinguish "never attempted" from "attempted and failed"

**Effort:** 1 hour (DDL change + plan update)

**Risk:** Low

---

### Option 2: Simplify to 2-state boolean

**Approach:** `embedded BOOLEAN NOT NULL DEFAULT FALSE` — simpler than 5 states, still distinguishes attempted from not.

**Effort:** 45 minutes

**Risk:** Low

---

## Technical Details

**Affected files:**
- `scripts/setup_pgvector.py` — DDL
- `production_opportunity_pipeline.py` — INSERT statement
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — schema section

## Acceptance Criteria

- [ ] Either `embedding_status` is removed (use `WHERE embedding IS NULL`) OR reduced to 2 states
- [ ] ON CONFLICT clause handles the simplified approach correctly
- [ ] HNSW partial index covers the primary query pattern

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
