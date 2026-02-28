---
status: pending
priority: p2
issue_id: "017"
tags: [code-review, security, credentials, github]
dependencies: []
---

# .env.tpl committed to public GitHub exposes 1Password vault names and Xeon internal IPs

## Problem Statement

`.env.tpl` is tracked in git (with `!.env.tpl` exception in `.gitignore`) and already pushed to the public GitHub remote. It contains specific 1Password vault names (`TrueNAS Infrastructure`), 1Password item names (`Anthropic API Key`, `Workspace Secrets`), and all Xeon service ports (`neo4j:7687`, `qdrant:6333`, `redis:6379`, `chromadb:8000`). The plan proposes adding `PG_*` variables to this file, which would add Postgres to the public infrastructure map.

## Findings

- `op://TrueNAS Infrastructure/Anthropic API Key/credential` — vault name and item name exposed
- `NEO4J_URI=bolt://10.0.0.87:7687` — internal IP and port exposed
- `REDIS_URL=redis://10.0.0.87:6379` — internal IP and port exposed
- File is publicly accessible on GitHub as `isndotbiz/opportunity-bot`
- The 1Password vault name narrows an attacker's search from all vaults to one
- Adding `PG_HOST=10.0.0.87`, `PG_USER=...` to `.env.tpl` extends the public attack map to include pgvector
- Review source: Security Sentinel (P2-A)

## Proposed Solutions

### Option 1: Replace specific values with generic placeholders

**Approach:**
```bash
# Replace in .env.tpl:
# Before: op://TrueNAS Infrastructure/Anthropic API Key/credential
# After:  op://<YOUR_VAULT_NAME>/<YOUR_ITEM_NAME>/credential

# Before: bolt://10.0.0.87:7687
# After:  bolt://<YOUR_XEON_IP>:7687
```

**Effort:** 30 minutes + force push to update remote

**Risk:** Medium — requires force-push to update the committed `.env.tpl`

---

### Option 2: Move .env.tpl to docs and remove git tracking

**Approach:** Stop tracking `.env.tpl` in git. Document connection string formats in `docs/setup.md` instead.

**Effort:** 1 hour

**Risk:** Low

---

## Technical Details

**Affected files:**
- `.env.tpl` — replace specific values with generic placeholders
- `.gitignore` — potentially remove `!.env.tpl` exception

## Acceptance Criteria

- [ ] `.env.tpl` contains no specific vault names, item names, or internal IPs
- [ ] Placeholders use `<YOUR_VAULT_NAME>`, `<YOUR_XEON_IP>` format
- [ ] `PG_*` variables added to `.env.tpl` use generic placeholders

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
