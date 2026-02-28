---
status: pending
priority: p3
issue_id: "035"
tags: [code-review, security, file-permissions, pii]
dependencies: []
---

# reports/advisor/latest.json contains financial PII with no access controls

## Problem Statement

`reports/advisor/latest.json` will contain personal FICO score, SBSS score, and credit tier. On the Xeon Linux server, files are created at mode `0644` (world-readable) by default. Any other user on the system can read this file. The plan proposes atomic rename via `tempfile.NamedTemporaryFile`, which creates the temp file at `0600`, but if `latest.json` already exists from a previous run, the rename behavior may inherit the destination's permissions.

## Findings

- `AdvisoryReport` includes `personal_fico: int | None`, `sbss: int | None`, `credit_tier: str` — financial PII
- `tempfile.NamedTemporaryFile` → `0600` permissions on the temp file
- `tmp_path.replace(path)` — on Linux, `os.rename()` preserves the source file's permissions (`0600`)
- However: first-ever creation is fine; if a different process ever writes `latest.json` at `0644`, subsequent atomic renames from `0600` temp file will set it to `0600` (correct)
- The plan does not explicitly set permissions or document the expected mode
- `reports/` is in `.gitignore` per plan — correct
- Review source: Security Sentinel (P2-D)

## Proposed Solutions

### Option 1: Explicitly chmod after atomic rename

```python
tmp_path.replace(path)
path.chmod(0o600)  # ensure world-unreadable regardless of umask
```

**Effort:** 5 minutes

**Risk:** None

---

### Option 2: Set UMask in systemd unit

Add `UMask=077` to the `[Service]` section. All files created by the service will be `0600`.

**Effort:** 10 minutes

**Risk:** Low

## Acceptance Criteria

- [ ] `reports/advisor/latest.json` is created with mode `0600` (not world-readable)
- [ ] Either explicit `chmod` after atomic rename or `UMask=077` in systemd unit

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
