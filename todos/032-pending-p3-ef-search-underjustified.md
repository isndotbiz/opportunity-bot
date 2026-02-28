---
status: pending
priority: p3
issue_id: "032"
tags: [code-review, database, pgvector, performance]
dependencies: ["007"]
---

# ef_search=100 underjustified — ef_search=40 sufficient for >95% recall at 10K docs

## Problem Statement

The plan sets `SET LOCAL hnsw.ef_search = 100` for advisor queries. At 10,000 documents with the corrected `m=16` index, `ef_search=40` achieves >95% recall. `ef_search=100` adds unnecessary graph traversal with no measurable recall improvement at this scale. The value should be noted as a starting point to tune downward via `EXPLAIN ANALYZE`.

## Findings

- Plan sets `ef_search=100` unconditionally for all advisor queries
- pgvector default: `ef_search=40`; appropriate for >95% recall at moderate scale
- At 10K docs with m=16: `ef_search=40` → >95% recall; `ef_search=100` → ~96% recall (unmeasurable improvement in practice)
- Review source: Performance Oracle (P3-C)

## Proposed Solutions

### Option 1: Change to ef_search=40 with tuning note

```sql
-- For week-1 (< 10K docs): ef_search=40 provides >95% recall
SET LOCAL hnsw.ef_search = 40;
-- Tune upward if advisor results feel irrelevant (check with EXPLAIN ANALYZE)
```

**Effort:** 5 minutes

**Risk:** None

## Acceptance Criteria

- [ ] `ef_search` default in advisor queries is ≤60
- [ ] Plan notes the tuning relationship: "increase ef_search if recall degrades"

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
