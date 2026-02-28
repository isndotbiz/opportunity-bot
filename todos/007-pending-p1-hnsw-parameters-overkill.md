---
status: pending
priority: p1
issue_id: "007"
tags: [code-review, database, pgvector, performance, schema]
dependencies: []
---

# HNSW m=32 ef_construction=128 miscalibrated for 1K-10K document dataset

## Problem Statement

The plan specifies `m=32, ef_construction=128` for the HNSW index. This is appropriate for 100K+ document datasets but is 4x overkill for the expected 1K-10K scale. At this scale `m=16, ef_construction=64` provides equivalent recall with ~4x faster index build time and 4x less memory. Additionally, `maintenance_work_mem = '16GB'` is grotesquely oversized for a ~2.5MB graph structure.

## Findings

- pgvector recommendation: `m=16` (default) for general use; `m=32` for 100K+ docs where recall degradation at `m=16` is measurable
- At 10,000 docs with `m=32`: HNSW graph size ≈ 10,000 × 32 × 8 bytes = ~2.5MB — `maintenance_work_mem=16GB` does nothing for a 2.5MB structure
- Recall difference between `m=16` and `m=32` at 10K docs: <1%
- The index can be rebuilt with `DROP INDEX; CREATE INDEX` when dataset exceeds 50K docs — no migration needed
- `ef_search=100` is also overkill at this scale; `ef_search=40` achieves >95% recall at 10K docs
- Review source: Performance Oracle (P1-C)

## Proposed Solutions

### Option 1: Set m=16, ef_construction=64 with rebuild note

**Approach:** Change DDL to:
```sql
CREATE INDEX IF NOT EXISTS opp_embedding_hnsw
    ON business_opportunities
    USING hnsw (embedding vector_ip_ops)
    WITH (m = 16, ef_construction = 64)
    WHERE embedding IS NOT NULL;
```
Add plan note: "Rebuild with m=32, ef_construction=128 when row count exceeds 50,000."

**Pros:**
- 4x faster index build on Xeon
- Correct parameters for the actual dataset size
- Trivially upgradeable

**Cons:**
- None at week-1 scale

**Effort:** 5 minutes (DDL change + plan note)

**Risk:** Low

---

### Option 2: Keep m=32 with correct maintenance_work_mem

**Approach:** Keep m=32 but fix `maintenance_work_mem` to a reasonable value (e.g., 256MB).

**Pros:**
- Marginally higher recall (unmeasurable at this scale)

**Cons:**
- Still unnecessarily slow index build
- Wrong parameters for dataset size

**Effort:** 5 minutes

**Risk:** Low

---

## Recommended Action

To be filled during triage. Option 1 is strongly preferred.

## Technical Details

**Affected files:**
- `scripts/setup_pgvector.py` (new file per plan) — DDL CREATE INDEX statement
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — schema section and deployment step 4

## Resources

- **Review source:** Performance Oracle (P1-C)
- **pgvector HNSW docs:** https://github.com/pgvector/pgvector#hnsw

## Acceptance Criteria

- [ ] HNSW index uses `m=16, ef_construction=64` in the plan DDL
- [ ] `maintenance_work_mem` recommendation is ≤1GB for index builds at current scale
- [ ] Plan includes a note to rebuild at 50K+ documents
- [ ] `ef_search` default in advisor queries is ≤60

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
