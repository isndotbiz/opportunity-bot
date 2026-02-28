---
status: pending
priority: p3
issue_id: "031"
tags: [code-review, security, deployment, postgresql]
dependencies: ["010"]
---

# PostgreSQL superuser (postgres) used throughout deployment — no least-privilege role

## Problem Statement

All deployment verification commands use `-U postgres`. If `PG_USER=postgres` ends up in `.env`, the application runs with PostgreSQL superuser privileges. A SQL injection or credential leak would have `SUPERUSER` access to every database on the Xeon. The principle of least privilege requires a dedicated application user with only the permissions needed.

## Findings

- Deployment steps 1, 3, 4, 8, 12, 20, 21, 22: all use `-U postgres`
- Plan does not include a step to create a least-privilege application role
- If `PG_USER` env var defaults to `postgres`, the application is a superuser
- Rollback procedure also uses `postgres` for `DROP TABLE IF EXISTS`
- Review source: Security Sentinel (P3-C)

## Proposed Solutions

### Option 1: Create opportunity_bot_app role with minimum permissions (see todo 010)

```sql
CREATE USER opportunity_bot_app WITH PASSWORD '...';
GRANT CONNECT ON DATABASE opportunity_bot TO opportunity_bot_app;
GRANT USAGE ON SCHEMA public TO opportunity_bot_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE business_opportunities TO opportunity_bot_app;
GRANT USAGE, SELECT ON SEQUENCE business_opportunities_id_seq TO opportunity_bot_app;
```

Keep `-U postgres` for admin-only steps (creating extensions, creating the role, creating the database). Use `-U opportunity_bot_app` for all application-level steps.

**Effort:** 30 minutes (combined with todo 010)

**Risk:** Low

## Acceptance Criteria

- [ ] A dedicated `opportunity_bot_app` PostgreSQL role exists with minimum permissions
- [ ] `PG_USER=opportunity_bot_app` in `.env` (not `postgres`)
- [ ] The application cannot `DROP TABLE`, `CREATE EXTENSION`, or access other databases

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
