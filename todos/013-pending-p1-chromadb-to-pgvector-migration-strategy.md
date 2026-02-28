---
status: pending
priority: p1
issue_id: "013"
tags: [code-review, deployment, migration, data]
dependencies: ["010", "012"]
---

# No ChromaDB-to-pgvector data migration strategy — existing data fate undocumented

## Problem Statement

The deployment checklist runs `--demo` to test the new pgvector installation but never addresses what happens to existing ChromaDB data. After deployment, pgvector starts completely empty. If existing ChromaDB opportunities have value (non-demo entries, scored opportunities), they are lost. The plan does not document whether existing data should be migrated or discarded.

## Findings

- Existing ChromaDB collection `business_opportunities` at Xeon (10.0.0.87:8000) contains scraped opportunities
- Plan step 15: `python3 production_opportunity_pipeline.py --demo` — tests with demo data only
- No migration script is planned or mentioned
- The plan notes "39% existing data is duplicate demo entries" but does not address the other 61%
- ChromaDB embeddings are not directly compatible with pgvector `vector(384)` columns — they would need re-encoding
- Review source: Deployment Verification Agent (P1-E)

## Proposed Solutions

### Option 1: Explicit discard decision (simplest for week-1)

**Approach:** Add to the deployment checklist:
```
# DATA MIGRATION DECISION
# DECISION: Existing ChromaDB data is discarded.
# Reason: ChromaDB embeddings use a different model/format and cannot be directly imported.
# First pgvector data comes from the first production scrape run after deployment.
# IMPACT: Query results are zero until first production run completes (~20 min).
```

**Pros:**
- Honest and simple
- No migration script to write and debug
- First production run repopulates with fresh, correctly-formatted data

**Cons:**
- Existing scored opportunities lost (they will be re-scraped and re-scored on next run)

**Effort:** 15 minutes (documentation only)

**Risk:** Low

---

### Option 2: Write a migration script

**Approach:** Export from ChromaDB → transform → import to pgvector with fresh embeddings.

**Pros:**
- Preserves historical scoring data

**Cons:**
- ChromaDB export format requires parsing
- Embeddings must be regenerated (not directly transferable)
- Significant development effort for week-1

**Effort:** 4-8 hours

**Risk:** Medium

---

## Recommended Action

To be filled during triage. Option 1 (explicit discard) is appropriate for week-1.

## Technical Details

**Affected files:**
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — add migration decision to deployment checklist

## Resources

- **Review source:** Deployment Verification Agent (P1-E)

## Acceptance Criteria

- [ ] Deployment checklist explicitly documents the migration decision (migrate or discard)
- [ ] If discard: a note warns that query results will be empty until first production run
- [ ] If migrate: a migration script is written and tested against a ChromaDB backup

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
