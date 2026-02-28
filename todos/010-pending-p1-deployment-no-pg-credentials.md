---
status: pending
priority: p1
issue_id: "010"
tags: [code-review, deployment, postgresql, credentials]
dependencies: []
---

# Deployment checklist missing PostgreSQL role/database/credentials creation steps

## Problem Statement

The 34-step deployment checklist jumps from "install pgvector" (step 3) to "run setup_pgvector.py" (step 10) without creating the PostgreSQL role, database, or credentials. `config_db.py` raises `KeyError` on any missing `PG_HOST`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE` environment variable. The deployment will fail silently at first database access. `.env.tpl` currently has no `PG_*` variables at all.

## Findings

- `config_db.py` uses `os.environ['PG_HOST']` (raises `KeyError` if missing, by design)
- `.env.tpl` has no `PG_*` variables in the current committed version
- No checklist step creates the PostgreSQL role, database, or grants permissions
- No checklist step writes `PG_*` variables to the Xeon's `.env` file
- No smoke test verifies the connection before running `setup_pgvector.py`
- Review source: Deployment Verification Agent (P1-D)

## Proposed Solutions

### Option 1: Add PG setup steps to deployment checklist (between steps 7 and 10)

**Approach:** Add these steps to the deployment checklist:
```bash
# 8a. Create PG role (least-privilege)
ssh user@10.0.0.87 "psql -U postgres -c \"CREATE USER opportunity_bot WITH PASSWORD 'CHANGEME';\""
ssh user@10.0.0.87 "psql -U postgres -c \"CREATE DATABASE opportunity_bot OWNER opportunity_bot;\""
ssh user@10.0.0.87 "psql -U postgres -c \"GRANT ALL ON DATABASE opportunity_bot TO opportunity_bot;\""

# 8b. Write PG credentials to .env on Xeon (use 1Password op:// refs in production)
ssh user@10.0.0.87 "cat >> /opt/opportunity-research-bot/.env << 'EOF'
PG_HOST=10.0.0.87
PG_PORT=5432
PG_DATABASE=opportunity_bot
PG_USER=opportunity_bot
PG_PASSWORD=CHANGEME
EOF"

# 8c. Smoke test the connection
ssh user@10.0.0.87 "psql -h localhost -U opportunity_bot -d opportunity_bot -c 'SELECT 1;'"
# Expected: " ?column? \n----------\n        1"
```

Also add `PG_*` variable entries to `.env.tpl`:
```
PG_HOST=op://TrueNAS Infrastructure/Xeon PostgreSQL/host
PG_PORT=5432
PG_DATABASE=opportunity_bot
PG_USER=op://TrueNAS Infrastructure/Xeon PostgreSQL/username
PG_PASSWORD=op://TrueNAS Infrastructure/Xeon PostgreSQL/password
```

**Pros:**
- Complete deployment procedure
- Uses least-privilege role (not `postgres` superuser)

**Cons:**
- Requires choosing a real password and adding to 1Password

**Effort:** 30 minutes

**Risk:** Low

---

## Recommended Action

To be filled during triage.

## Technical Details

**Affected files:**
- `.env.tpl` — add PG_* variables
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — update deployment checklist

## Resources

- **Review source:** Deployment Verification Agent (P1-D); Security Sentinel (P3-C)

## Acceptance Criteria

- [ ] Deployment checklist includes PG role creation step
- [ ] Deployment checklist includes credential writing to .env
- [ ] Deployment checklist includes connection smoke test
- [ ] `.env.tpl` has `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD` entries
- [ ] Application uses `opportunity_bot` role, not `postgres` superuser

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
