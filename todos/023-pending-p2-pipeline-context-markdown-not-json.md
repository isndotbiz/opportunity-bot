---
status: pending
priority: p2
issue_id: "023"
tags: [code-review, agent-native, data-format]
dependencies: []
---

# data/pipeline_context.md is Markdown — agents cannot parse it reliably

## Problem Statement

The plan specifies `data/pipeline_context.md` as an inter-run context file written at the end of each pipeline run. An orchestrating agent reading this file to determine system state must parse free-form Markdown text. The completion signal `reports/runs/latest.json` is already JSON — there is no reason the context file should be a different format. Markdown is for humans; JSON is for agents.

## Findings

- Plan specifies the file as `.md` with Markdown headers and bullet points
- Agents parsing this file must regex-parse free-form text (fragile; format changes break parsing silently)
- `reports/runs/latest.json` is correctly JSON — inconsistency in the plan
- The content maps directly to a JSON schema: last_run_at, sources dict, new_stored, cache_hits, db_total, etc.
- Review source: Agent-Native Reviewer (P2-5)

## Proposed Solutions

### Option 1: Change to data/pipeline_context.json

```python
context = {
    "last_run_at": datetime.now(timezone.utc).isoformat(),
    "sources": {"reddit": 42, "hn": 31, "ph": 28, "ih": 19},
    "new_stored": 101,
    "cache_hits": 89,
    "skipped_duplicates": 67,
    "db_total": 1847,
    "db_host": f"{os.environ.get('PG_HOST', 'unknown')}:5432",
    "credit_tier": profile.risk_tier if profile else None,
}
with open('data/pipeline_context.json', 'w') as f:
    json.dump(context, f, indent=2)
```

**Effort:** 30 minutes

**Risk:** Low

---

## Technical Details

**Affected files:**
- `production_opportunity_pipeline.py` — `complete_pipeline_run()` function
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — agent-native section

## Acceptance Criteria

- [ ] Context file is `data/pipeline_context.json` (not `.md`)
- [ ] Schema is documented in the plan
- [ ] An agent can `json.load()` the file and access `last_run_at`, `db_total`, `cache_hits` without regex parsing

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
