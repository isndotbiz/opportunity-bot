---
status: pending
priority: p2
issue_id: "015"
tags: [code-review, python, dead-code, config]
dependencies: []
---

# get_db_settings() is dead code with contradictory silent defaults

## Problem Statement

The proposed `config_db.py` includes a `get_db_settings()` function that returns a dict with host, port, database, and storage type. No caller is shown in the plan. More critically, it uses `os.environ.get('PG_HOST', '10.0.0.87')` (silent defaults) while `get_pgvector_connection()` uses `os.environ['PG_HOST']` (loud KeyError on missing vars). If any caller ever passes `get_db_settings()` output to the connection factory, the hardcoded defaults create a discrepancy.

## Findings

- `get_db_settings()` returns `{'host': os.environ.get('PG_HOST', '10.0.0.87'), ...}` — silent default
- `get_pgvector_connection()` uses `os.environ['PG_HOST']` — intentionally loud
- No caller shown in the plan — this function is dead code from the first line
- Inconsistent behavior: `get_db_settings()` claims the host is `10.0.0.87` even when env var is missing; connection factory would raise `KeyError`
- Review source: Kieran Python Reviewer (P2-8); Code Simplicity Reviewer (P2-S10)

## Proposed Solutions

### Option 1: Delete get_db_settings() entirely

**Approach:** Remove the function from `config_db.py`. If display of connection info is needed at pipeline startup, log `os.environ.get('PG_HOST', '<not set>')` inline.

**Effort:** 5 minutes

**Risk:** Low

---

### Option 2: Make it consistent with the connection factory

**Approach:** Use `os.environ['PG_HOST']` (no default) in `get_db_settings()` too. Add a docstring explaining its purpose (display only, never used for actual connection).

**Effort:** 10 minutes

**Risk:** Low

---

## Technical Details

**Affected files:**
- `config_db.py` (new file per plan) — `get_db_settings()` function

## Acceptance Criteria

- [ ] Either `get_db_settings()` is removed from `config_db.py`, OR it uses consistent behavior with `get_pgvector_connection()`
- [ ] If retained, at least one caller is identified in the plan

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
