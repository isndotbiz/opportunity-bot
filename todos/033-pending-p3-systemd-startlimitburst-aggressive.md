---
status: pending
priority: p3
issue_id: "033"
tags: [code-review, deployment, systemd, operations]
dependencies: ["019"]
---

# systemd StartLimitBurst=3 exhausted before PostgreSQL cold-start completes

## Problem Statement

The systemd unit has `RestartSec=30s` and `StartLimitBurst=3`. If PostgreSQL on the Xeon takes 2 minutes to start (cold boot), the service attempts 3 restarts in 90 seconds, exhausts its budget, and enters `failed` state. Recovering requires manual `systemctl reset-failed && systemctl start opportunity-bot`. A pre-start health check for PostgreSQL readiness would prevent this.

## Findings

- 3 restarts × 30s each = 90s before `failed`; PostgreSQL cold start can take 2+ minutes
- systemd unit has no `ExecStartPre` health check for PostgreSQL availability
- No `pg_isready` check before the main process starts
- `After=postgresql.service` assumes local PostgreSQL; pgvector is on 10.0.0.87 (remote)
- Review source: Deployment Verification Agent (P3-C, P3-B)

## Proposed Solutions

### Option 1: Add ExecStartPre with pg_isready + increase burst limit

```ini
[Service]
ExecStartPre=/bin/bash -c 'until pg_isready -h 10.0.0.87 -p 5432; do sleep 5; done'
StartLimitBurst=5
StartLimitIntervalSec=600
```

**Effort:** 15 minutes

**Risk:** Low

---

### Option 2: Increase StartLimitBurst without health check

**Approach:** Change to `StartLimitBurst=10, StartLimitIntervalSec=600` to give PostgreSQL time to come up.

**Effort:** 5 minutes

**Risk:** Low (slightly less safe than Option 1)

## Acceptance Criteria

- [ ] Service does not enter `failed` state on Xeon cold boot before PostgreSQL is ready
- [ ] Either `ExecStartPre` health check or higher `StartLimitBurst` value
- [ ] Plan notes that `After=postgresql.service` only applies if PostgreSQL is local

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
