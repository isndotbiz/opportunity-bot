---
status: pending
priority: p1
issue_id: "008"
tags: [code-review, security, pii, git-history, urgent]
dependencies: []
---

# test_isnbiz.json on GitHub remote — force push alone insufficient, needs GitHub Support GC

## Problem Statement

`credit_integration/profiles/test_isnbiz.json` was committed in commit `4558a05` and pushed to the GitHub remote. It contains Equifax business ID 722429197, credit score 372, and full tradeline data. The plan proposes `git filter-repo` + `git push --force`, but GitHub caches repository objects for up to 90 days after force-push. The data remains accessible until GitHub Support triggers garbage collection. The plan's remediation is incomplete.

## Findings

- Commit `4558a05` ("Opportunity Bot - FICO Personalization System") pushed `test_isnbiz.json` to the remote
- `credit_integration/profiles/` is NOT in `.gitignore`
- GitHub retains objects after force-push until GC is triggered by support request
- The file is currently accessible via the GitHub raw URL or via `git show 4558a05:credit_integration/profiles/test_isnbiz.json` on any clone
- Anyone who cloned the repo before the force-push still has the data locally
- Review source: Deployment Verification Agent (P1-B); Security Sentinel (P1-A)

## Proposed Solutions

### Option 1: Filter-repo + GitHub Support GC request (complete remediation)

**Approach:**
```bash
# 1. Purge from local history
pip install git-filter-repo
git filter-repo --path credit_integration/profiles/ --invert-paths --force

# 2. Add to .gitignore BEFORE pushing
echo "credit_integration/profiles/" >> .gitignore
git add .gitignore
git commit -m "security: exclude credit profiles from git tracking"

# 3. Force push (overwrites remote history)
git push origin main --force

# 4. Contact GitHub Support
# Go to: https://support.github.com/contact
# Request: "Please run garbage collection on isndotbiz/opportunity-bot to purge cached objects after history rewrite"

# 5. Verify the file is gone from history
git log --all --oneline -- "credit_integration/profiles/test_isnbiz.json"
# Should return no output
```

**Pros:**
- Complete remediation when combined with GitHub Support GC
- Correct procedure

**Cons:**
- GitHub GC request may take 1-3 business days
- Any collaborator clones must be re-cloned after force-push

**Effort:** 30 minutes (plus GitHub Support wait time)

**Risk:** Low (file is not financally rotatable — Equifax business ID is permanent — but limiting exposure is correct)

---

## Recommended Action

To be filled during triage. This is the FIRST task to complete before any other work.

## Technical Details

**Affected files:**
- `credit_integration/profiles/test_isnbiz.json` — must be purged from git history
- `.gitignore` — must add `credit_integration/profiles/`
- `credit_integration/profiles/` — move output path to `~/.opportunity-bot/profiles/` per plan

## Resources

- **Commit:** `4558a05`
- **GitHub GC request:** https://support.github.com/contact
- **git-filter-repo:** https://github.com/newren/git-filter-repo
- **Review source:** Security Sentinel (P1-A); Deployment Verification Agent

## Acceptance Criteria

- [ ] `git log --all -- credit_integration/profiles/` returns no output
- [ ] `credit_integration/profiles/` added to `.gitignore`
- [ ] GitHub Support GC request submitted
- [ ] Force push executed
- [ ] All collaborator clones warned to re-clone

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)

**Actions:**
- Confirmed commit 4558a05 pushed test_isnbiz.json to remote
- Identified that force push alone is insufficient without GitHub GC
- Documented complete remediation procedure
