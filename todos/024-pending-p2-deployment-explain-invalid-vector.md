---
status: pending
priority: p2
issue_id: "024"
tags: [code-review, deployment, postgresql, pgvector]
dependencies: []
---

# Deployment EXPLAIN query uses invalid placeholder vector — will fail with parse error

## Problem Statement

Deployment checklist step 20 uses `ORDER BY embedding <#> '[0.1,0.2,...]'::vector` to verify the HNSW index. `'[0.1,0.2,...]'` is not valid pgvector syntax — the `...` placeholder is not 384 float values. This will produce a parse error, not an EXPLAIN output. An operator may assume the check passed when it actually failed.

## Findings

- Step 20: `EXPLAIN SELECT id FROM business_opportunities ORDER BY embedding <#> '[0.1,0.2,...]'::vector LIMIT 5;`
- pgvector requires exactly N float values (N=384 for all-MiniLM-L6-v2)
- `'[0.1,0.2,...]'` → PostgreSQL parse error: invalid input
- The operator may interpret the error as "index check inconclusive" rather than "command is broken"
- Review source: Deployment Verification Agent (P2-B)

## Proposed Solutions

### Option 1: Use vector_dims() or an existing embedding for verification

```sql
-- Option A: Check dimensions of an existing embedding
SELECT DISTINCT vector_dims(embedding) FROM business_opportunities WHERE embedding IS NOT NULL;
-- Expected: single row with value 384

-- Option B: Use EXPLAIN with a query that references an existing vector
EXPLAIN SELECT id FROM business_opportunities
ORDER BY embedding <#> (SELECT embedding FROM business_opportunities LIMIT 1)
LIMIT 5;
-- Look for "Index Scan using opp_embedding_hnsw" in the output

-- Option C: Generate a zero vector of correct dimension
EXPLAIN SELECT id FROM business_opportunities
ORDER BY embedding <#> array_fill(0.0::float4, ARRAY[384])::vector
LIMIT 5;
```

**Effort:** 15 minutes

**Risk:** Low

---

## Technical Details

**Affected files:**
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — deployment step 20

## Acceptance Criteria

- [ ] Step 20 EXPLAIN query is syntactically valid and executes without error
- [ ] The query verifies HNSW index is being used (look for "Index Scan using opp_embedding_hnsw")

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
