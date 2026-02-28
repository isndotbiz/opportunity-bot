---
status: pending
priority: p1
issue_id: "011"
tags: [code-review, deployment, pgvector, schema]
dependencies: []
---

# pgvector version never asserted after install — hnsw.iterative_scan will fail if < 0.8.0

## Problem Statement

The deployment checklist checks whether the pgvector extension is _available_ but never asserts the installed version. If the Xeon has an older pgvector (e.g., 0.5.x), `hnsw.iterative_scan = 'relaxed_order'` in the advisor queries will fail with a PostgreSQL error at runtime, not at deployment time. The plan requires pgvector >= 0.8.0 for this feature.

## Findings

- Plan deployment step 2: checks `SELECT * FROM pg_available_extensions WHERE name = 'vector'`
- Plan deployment step 3: installs from source pinned to v0.8.0
- But: no assertion after `make install && make install` that the version actually changed
- If old pgvector already installed via `apt`, `make install` may not override it
- `SET LOCAL hnsw.iterative_scan = 'relaxed_order'` in advisor SQL → `ERROR: unrecognized configuration parameter` on pgvector < 0.8.0
- Review source: Deployment Verification Agent (P1-A); Code Simplicity Reviewer (P1-S3)

## Proposed Solutions

### Option 1: Add version assertion step after install + remove SET LOCAL for week-1

**Approach:** Add between steps 3 and 4:
```sql
SELECT extversion FROM pg_extension WHERE extname = 'vector';
-- Required: 0.8.0 or higher
-- If lower: DROP EXTENSION vector CASCADE; CREATE EXTENSION vector;
```

AND in the advisor SQL, gate `SET LOCAL hnsw.iterative_scan` behind a version check:
```python
# Only use iterative_scan if pgvector >= 0.8.0
# For week-1, remove SET LOCAL hnsw.iterative_scan entirely
# Add comment: # Enable when table exceeds 10K rows and pgvector >= 0.8.0 confirmed
```

**Pros:**
- Deployment fails fast if wrong version
- Advisor works correctly on any pgvector version

**Cons:**
- Slightly less optimal filtered queries on older pgvector (not measurable at week-1 scale)

**Effort:** 30 minutes

**Risk:** Low

---

### Option 2: Pin to 0.8.0 and assert strictly

**Approach:** Assert exact version in deployment; fail if not 0.8.0+.

**Pros:**
- Guarantees all features available

**Cons:**
- Install from source is more complex on some Xeon OS versions

**Effort:** 1-2 hours

**Risk:** Medium

---

## Recommended Action

To be filled during triage.

## Technical Details

**Affected files:**
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — deployment steps 2-3 and advisor SQL

## Resources

- **Review source:** Deployment Verification Agent (P1-A); Code Simplicity Reviewer (P1-S3)

## Acceptance Criteria

- [ ] Deployment checklist asserts `SELECT extversion FROM pg_extension WHERE extname = 'vector'` returns `0.8.0` or higher
- [ ] Advisor SQL that uses `hnsw.iterative_scan` is either gated on version check or removed for week-1
- [ ] Deployment checklist fails explicitly (not silently) if pgvector < 0.8.0

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
