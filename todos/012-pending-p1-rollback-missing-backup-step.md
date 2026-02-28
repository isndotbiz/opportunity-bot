---
status: pending
priority: p1
issue_id: "012"
tags: [code-review, deployment, rollback, config-chromadb]
dependencies: []
---

# Deployment rollback not executable — config_chromadb.py backup step missing from checklist

## Problem Statement

The deployment rollback procedure (step 23) says "If you made a backup before starting: `cp /backup/config_chromadb.py .`" — but there is no backup step in the pre-deploy checklist. Since `config_chromadb.py` was never committed to git, `git checkout HEAD -- config_chromadb.py` fails. If the migration goes wrong and the operator has not manually backed up the file, the rollback path requires recreating the file from memory during a live incident.

## Findings

- `config_chromadb.py` has `?? config_chromadb.py` status — never committed, only in working tree
- `git log --oneline -- config_chromadb.py` returns nothing
- Rollback step 23 assumes a backup exists without creating it
- `config_chromadb.py` is the ChromaDB failover logic — without it, rollback to ChromaDB is blocked
- Review source: Deployment Verification Agent (P1-B); git-history-analyzer (Round 2)

## Proposed Solutions

### Option 1: Add backup step to pre-deploy checklist

**Approach:** Add as step 8a (before stopping the pipeline):
```bash
# 8a. Backup untracked files required for rollback
cp config_chromadb.py /tmp/config_chromadb.py.bak
echo "Backup location: /tmp/config_chromadb.py.bak" | tee -a logs/pre_migration_baseline.txt

# Also commit it to git now so rollback can use git checkout
git add config_chromadb.py
git commit -m "chore: track config_chromadb.py for rollback safety"
```

**Pros:**
- Rollback step 23 becomes executable
- Committing the file to git makes the rollback idempotent

**Cons:**
- Committing a file we're planning to replace is slightly odd; add a comment explaining it's for rollback safety

**Effort:** 15 minutes

**Risk:** Low

---

### Option 2: Commit config_chromadb.py to git immediately (before migration planning)

**Approach:** Run `git add config_chromadb.py && git commit` before any migration work begins.

**Pros:**
- Always available via `git checkout HEAD -- config_chromadb.py`
- No separate backup needed

**Cons:**
- None

**Effort:** 5 minutes

**Risk:** Low

---

## Recommended Action

To be filled during triage. Option 2 (commit immediately) is strongly preferred.

## Technical Details

**Affected files:**
- `config_chromadb.py` — currently untracked; should be committed to git
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — add backup step to deployment checklist

## Resources

- **Review source:** Deployment Verification Agent (P1-B)

## Acceptance Criteria

- [ ] `config_chromadb.py` is committed to git OR a backup step is added to the pre-deploy checklist
- [ ] Deployment rollback step 23 is executable without manual file reconstruction
- [ ] Rollback procedure is tested (dry run) before live migration

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
