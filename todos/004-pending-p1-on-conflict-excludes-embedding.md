---
status: pending
priority: p1
issue_id: "004"
tags: [code-review, database, pgvector, embeddings]
dependencies: []
---

# ON CONFLICT DO UPDATE excludes embedding and embedding_status — retry mechanism broken

## Problem Statement

The proposed `ON CONFLICT (url) DO UPDATE SET` block updates analysis fields but NOT `embedding` or `embedding_status`. If a row already exists with `embedding_status = 'failed'`, re-scraping the same URL triggers the ON CONFLICT path but the embedding failure state is preserved forever. The plan documents `embedding_status` as a retry mechanism, but the UPDATE SET makes retrying via re-scraping impossible.

## Findings

- Proposed UPDATE SET includes: `automation_score`, `legitimacy_score`, `recommended_action`, `key_insights`, `risks`, `analysis_version`, `analyzed_at`
- NOT included: `embedding`, `embedding_status`, `embedding_error`
- A row with `embedding_status = 'failed'` will never be retried — the UPSERT leaves the failure state intact even when `analysis_version` is bumped
- Also: `title`, `initial_investment`, `initial_investment_min_usd` are excluded — corrections to scraped fields are silently ignored on re-scrape
- Review source: Kieran Python Reviewer (P1-4)

## Proposed Solutions

### Option 1: Reset embedding_status to 'pending' on analysis version bump

**Approach:** Add to the UPDATE SET clause:
```sql
embedding_status = 'pending',
embedding_error = NULL
```
This causes the next embedding pass to retry the failed row.

**Pros:**
- Minimal change
- Preserves the existing `embedding_status` 5-state design

**Cons:**
- Does not update the `embedding` vector itself (still needs a separate backfill pass)

**Effort:** 15 minutes

**Risk:** Low

---

### Option 2: Simplify to NULL-check and eliminate embedding_status

**Approach:** Drop `embedding_status` column (as the simplicity reviewer recommended). Check `WHERE embedding IS NULL` to find rows needing embeddings. The ON CONFLICT clause then only needs to update analysis fields; embedding backfill runs as a separate pass that reads `WHERE embedding IS NULL`.

**Pros:**
- Simpler schema
- Naturally retries any row missing an embedding

**Cons:**
- Cannot distinguish "never attempted" from "attempted and failed" without a separate flag

**Effort:** 1 hour (schema change + plan update)

**Risk:** Low-Medium

---

## Recommended Action

To be filled during triage.

## Technical Details

**Affected files:**
- `production_opportunity_pipeline.py` — proposed INSERT ... ON CONFLICT statement
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — plan lines 424-438

**Database changes:**
- If Option 1: No schema change, just update the SQL in the plan
- If Option 2: Remove `embedding_status` column from DDL

## Resources

- **Plan:** lines 424-438 (ON CONFLICT DO UPDATE spec)
- **Review source:** Kieran Python Reviewer (P1-4)

## Acceptance Criteria

- [ ] A row with `embedding_status = 'failed'` is retried on the next pipeline run
- [ ] OR: the schema uses `WHERE embedding IS NULL` instead of `embedding_status`
- [ ] The retry mechanism is testable without manual SQL intervention
- [ ] `analysis_version` bump correctly triggers re-embedding

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)

**Actions:**
- Identified embedding/embedding_status exclusion from ON CONFLICT UPDATE SET
- Traced the retry mechanism to show it is logically broken
- Proposed two resolution paths
