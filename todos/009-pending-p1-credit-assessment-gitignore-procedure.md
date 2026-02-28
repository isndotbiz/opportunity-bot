---
status: pending
priority: p1
issue_id: "009"
tags: [code-review, security, pii, git]
dependencies: ["008"]
---

# CREDIT_ASSESSMENT.md gitignore procedure wrong — must git rm --cached first

## Problem Statement

The plan's acceptance criteria includes "CREDIT_ASSESSMENT_*.md added to .gitignore." This is incorrect as written — `.gitignore` does not untrack files already tracked by git. `CREDIT_ASSESSMENT_2026-02-04.md` is already in the git index. Adding it to `.gitignore` will silently fail to protect it, and the file will still be committed on the next `git add .` or `git commit -a`.

## Findings

- `CREDIT_ASSESSMENT_2026-02-04.md` was committed locally (NOT yet pushed to GitHub remote per git log check)
- `.gitignore` has no entry for this file currently
- `git rm --cached` is required to untrack an already-tracked file; `.gitignore` alone is insufficient
- The file contains personal FICO scores 763-788 across three bureaus for a named individual — PII
- Review source: Security Sentinel (P1-B)

## Proposed Solutions

### Option 1: git rm --cached + .gitignore (correct procedure)

**Approach:**
```bash
# Step 1: Untrack the file (removes from git index, keeps on disk)
git rm --cached CREDIT_ASSESSMENT_2026-02-04.md

# Step 2: Add pattern to .gitignore
echo "CREDIT_ASSESSMENT_*.md" >> .gitignore

# Step 3: Commit the untracking
git add .gitignore
git commit -m "security: untrack credit assessment PII document"

# Step 4: Verify the file is no longer tracked
git status  # CREDIT_ASSESSMENT_2026-02-04.md should appear as untracked
git ls-files CREDIT_ASSESSMENT_2026-02-04.md  # should return nothing
```

**Pros:**
- Correct procedure — file stops being tracked immediately
- File remains on disk for use by the application

**Cons:**
- Does NOT remove from local git history (use `git filter-repo` if that's also needed)

**Effort:** 10 minutes

**Risk:** Low

---

## Recommended Action

To be filled during triage. Must be completed before any `git add` or `git push` operations.

## Technical Details

**Affected files:**
- `CREDIT_ASSESSMENT_2026-02-04.md` — must be untracked
- `.gitignore` — must add `CREDIT_ASSESSMENT_*.md` pattern

## Resources

- **Review source:** Security Sentinel (P1-B)

## Acceptance Criteria

- [ ] `git ls-files CREDIT_ASSESSMENT_2026-02-04.md` returns empty
- [ ] `echo "test" >> CREDIT_ASSESSMENT_2026-02-04.md && git status` shows the file as untracked (not modified)
- [ ] `.gitignore` contains `CREDIT_ASSESSMENT_*.md`
- [ ] File still exists on disk at its original path

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
