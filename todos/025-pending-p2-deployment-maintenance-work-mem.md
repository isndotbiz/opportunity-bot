---
status: pending
priority: p2
issue_id: "025"
tags: [code-review, deployment, postgresql, performance]
dependencies: []
---

# maintenance_work_mem SET is session-only — does not apply to setup_pgvector.py

## Problem Statement

Deployment step 4 sets `maintenance_work_mem = '16GB'` via `psql -c "SET ..."`. This applies only to that one `psql` session, which closes immediately. When `setup_pgvector.py` opens its own connection in step 10, it uses the default `maintenance_work_mem` (typically 64MB), making the HNSW index build dramatically slower. The plan intends 16GB to accelerate the index build but the timing means it has no effect.

## Findings

- `psql -c "SET maintenance_work_mem = '16GB';"` — applies to a single-connection session that closes immediately
- `python3 scripts/setup_pgvector.py` (step 10) — new connection, uses default `maintenance_work_mem`
- Step 12's `\set maintenance_work_mem '16GB'` inside the psql heredoc is correct for that step but too late (index created in step 10)
- Fix options: `ALTER SYSTEM SET` (persistent) or `SET LOCAL` inside `setup_pgvector.py` before `CREATE INDEX`
- Review source: Deployment Verification Agent (P2-D)

## Proposed Solutions

### Option 1: Move SET inside setup_pgvector.py

```python
# In scripts/setup_pgvector.py, before CREATE INDEX:
with get_pgvector_connection() as conn:
    cur = conn.cursor()
    cur.execute("SET maintenance_work_mem = '1GB'")  # 1GB is sufficient for <10K rows
    cur.execute("""CREATE INDEX IF NOT EXISTS opp_embedding_hnsw ...""")
```

**Effort:** 15 minutes

**Risk:** Low

---

### Option 2: ALTER SYSTEM + pg_reload_conf

```sql
ALTER SYSTEM SET maintenance_work_mem = '1GB';
SELECT pg_reload_conf();
```

**Pros:** Persists across connections. **Cons:** Changes system-level config permanently.

**Effort:** 10 minutes

**Risk:** Low-Medium (permanent system config change)

---

## Technical Details

**Affected files:**
- `scripts/setup_pgvector.py` — add SET maintenance_work_mem before CREATE INDEX
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — deployment steps 4 and 10

## Acceptance Criteria

- [ ] `maintenance_work_mem` is set in the same connection/session that runs CREATE INDEX
- [ ] Value is appropriate for dataset size (not 16GB for <10K rows)

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
