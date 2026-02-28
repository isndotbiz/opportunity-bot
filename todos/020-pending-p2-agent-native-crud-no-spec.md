---
status: pending
priority: p2
issue_id: "020"
tags: [code-review, agent-native, architecture, api]
dependencies: []
---

# Agent-native CRUD stubs have no file location, argument contracts, or delete_opportunity

## Problem Statement

The plan's "Agent-Native Patterns" section lists six callable functions (`scrape_source`, `analyze_opportunity`, `store_opportunity`, `search_opportunities`, `get_opportunity`, `update_opportunity`) as bullet-point stubs with no file location, no complete argument contracts, no return type contracts, and no `delete_opportunity`. An implementing agent has no canonical spec to code against and an orchestrating agent has nothing importable.

## Findings

- Six function stubs with no file ownership: no module assigned
- `raw: dict` and `filters: dict` have no specified key contracts
- `update_opportunity(doc_id, updates: dict)` accepts arbitrary updates — no field whitelist (allows corrupting embeddings)
- `delete_opportunity` is absent entirely
- `query_opportunities.py` is a `__main__` script — `search_opportunities()` is not importable
- No exit-code convention for any CLI tool (exit 0 on crash same as exit 0 on success)
- No pipeline running-state artifact (can't distinguish running from crashed)
- Review source: Agent-Native Reviewer (P1-1, P1-4, P2-7, P2-8)

## Proposed Solutions

### Option 1: Promote agent-native section to full spec with file ownership

**Approach:** Add a new plan section specifying `opportunity_api.py` as the canonical module:

```python
# opportunity_api.py — importable functions for agent orchestration

def scrape_source(source_name: str) -> dict:
    """Returns: {"records": list[ScrapedRecord], "scraped_count": int, "errors": list[str], "elapsed_s": float}"""

def get_opportunity(doc_id: str) -> dict | None:
    """Returns the opportunity row as dict, or None if not found."""

def update_opportunity(doc_id: str, updates: dict) -> bool:
    """Allowed keys: {"embedding_status", "analysis_version", "recommended_action"}. Returns True on success."""

def delete_opportunity(doc_id: str) -> bool:
    """Hard delete. Returns True on success."""

def search_opportunities(query: str, filters: dict | None = None, limit: int = 10) -> list[dict]:
    """filters: {"min_automation_score": int, "max_investment_usd": float, "source": str}"""
```

Also add `reports/runs/running.json` as in-flight state artifact.

**Effort:** 2-3 hours (plan update only)

**Risk:** Low

---

### Option 2: Keep as stubs but mark YAGNI for week-1

**Approach:** Move the agent-native section under the OUT OF SCOPE gate (same as todo 019).

**Effort:** 30 minutes

**Risk:** Low

---

## Technical Details

**Affected files:**
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — agent-native section

## Acceptance Criteria

- [ ] All callable functions have a file location (`opportunity_api.py` or similar)
- [ ] All argument types are specified (no bare `dict`)
- [ ] `delete_opportunity` is included
- [ ] `update_opportunity` has an explicit field whitelist
- [ ] `query_opportunities.py` is restructured with an importable function
- [ ] Exit-code convention documented for all CLI tools

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
