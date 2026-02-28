---
status: pending
priority: p2
issue_id: "019"
tags: [code-review, architecture, scope, yagni]
dependencies: []
---

# Xeon always-on daemon / systemd architecture in W1 scope — YAGNI for week-1

## Problem Statement

The plan includes a full "Xeon Always-On Architecture" section with systemd unit file, asyncio producer/consumer, Redis seen-URL dedup, and 4 parallel llama-server workers as part of the main plan body. This is week-2+ infrastructure for a daemon that doesn't yet exist. The north star is "$5+ income in week 1" — a cron-fired one-shot script is entirely sufficient. An implementer following the plan will build all of this before the first dollar.

## Findings

- "Xeon Always-On Architecture" section appears in the main plan body with no week-1 exclusion gate
- Includes: systemd unit file (5 stanzas), asyncio + ProcessPoolExecutor rewrite, Redis seen-URL dedup with TTL, 4 parallel llama-server instances with `numactl` pinning, graceful SIGTERM handling
- All of these appear in the 34-step deployment checklist (steps 27-34) as week-1 tasks
- The plan itself correctly says in "Step 1": "Keep one-shot script; add LLM cache and batch embeddings"
- The LLM cache already reduces the bottleneck to ~11 minutes — well within a daily cron window
- Review source: Code Simplicity Reviewer (P1-S1); also YAGNI analysis V1, V2

## Proposed Solutions

### Option 1: Add explicit OUT OF SCOPE gate to the always-on section

**Approach:** Add a callout box at the top of "Xeon Always-On Architecture":
```
> ⚠️ OUT OF SCOPE — WEEK 1
> This section describes the target state after the first $5 income is achieved.
> See docs/plans/future/xeon-daemon-architecture.md
> For week-1: use the one-shot cron script (W1 Step 1 approach).
```

And remove steps 27-34 from the main deployment checklist, moving them to a separate "Step 2 deployment" document.

**Effort:** 30 minutes (plan edit only)

**Risk:** Low

---

### Option 2: Create a separate future plan document

**Approach:** Move the entire "Xeon Always-On Architecture" section to `docs/plans/future/xeon-daemon-architecture-plan.md`.

**Effort:** 1 hour

**Risk:** Low

---

## Technical Details

**Affected files:**
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — add OUT OF SCOPE gate to daemon section, move checklist steps 27-34

## Acceptance Criteria

- [ ] The "Xeon Always-On Architecture" section is clearly marked as OUT OF SCOPE for week-1
- [ ] Deployment checklist steps 27-34 (daemon monitoring) are separated from steps 1-26 (week-1 deployment)
- [ ] Week-1 implementation path uses cron + one-shot script, not systemd daemon

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
