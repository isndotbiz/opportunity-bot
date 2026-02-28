---
status: pending
priority: p2
issue_id: "021"
tags: [code-review, database, schema, premature-optimization, yagni]
dependencies: []
---

# Four secondary indexes premature for week-1 row counts — PostgreSQL will use sequential scans anyway

## Problem Statement

The plan specifies four secondary B-Tree indexes in addition to the HNSW index: `opp_automation_score`, `opp_investment_automation` (composite), `opp_embedding_status`, and `opp_analysis_version`. At week-1 scale (hundreds to low thousands of rows), PostgreSQL's query planner will prefer sequential scans over any B-Tree index. These indexes add schema complexity, index build time in deployment, and maintenance overhead with zero query performance benefit.

## Findings

- PostgreSQL query planner uses sequential scans for tables under ~500-1000 rows (depends on row width and stats)
- At week-1 scale, the planner will ignore all four indexes regardless of query
- `opp_analysis_version WHERE analysis_version < 2`: covers every row (version starts at 1) until version-2 prompt is deployed — will never be used for targeted re-analysis
- `CREATE INDEX CONCURRENTLY` complexity adds a deployment step for unused indexes
- Review source: Code Simplicity Reviewer (P1-S4); Performance Oracle (P1-C)

## Proposed Solutions

### Option 1: Remove all four secondary indexes; add later when needed

**Approach:**
```sql
-- Keep only:
-- 1. HNSW index (semantic search)
-- 2. UNIQUE constraint on url (dedup)
-- 3. UNIQUE constraint on doc_id (if kept)

-- Remove from DDL:
-- CREATE INDEX opp_automation_score ...
-- CREATE INDEX opp_investment_automation ...
-- CREATE INDEX opp_embedding_status ...
-- CREATE INDEX opp_analysis_version ...
```

Add plan note: "Add filter indexes after `EXPLAIN ANALYZE` shows sequential scans causing visible latency (expected at ~5,000+ rows)."

**Effort:** 15 minutes (DDL change)

**Risk:** Low

---

## Technical Details

**Affected files:**
- `scripts/setup_pgvector.py` (new file) — DDL CREATE INDEX statements
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — schema section

## Acceptance Criteria

- [ ] Only the HNSW index and UNIQUE constraints are in the week-1 DDL
- [ ] Plan notes when to add filter indexes (e.g., "after EXPLAIN ANALYZE shows sequential scans at N rows")
- [ ] Deployment checklist `CREATE INDEX CONCURRENTLY` step is removed or deferred

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
