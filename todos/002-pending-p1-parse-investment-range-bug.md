---
status: pending
priority: p1
issue_id: "002"
tags: [code-review, python, data-corruption, advisor]
dependencies: []
---

# parse_investment_range() corrupts values with comma-separated amounts

## Problem Statement

The proposed `parse_investment_range()` helper function has a bug that silently corrupts investment range values containing thousands separators. `"$1,500-$2,000"` becomes `"$15002000"` before the regex runs, producing `(15002000.0, 15002000.0)` instead of `(1500.0, 2000.0)`. This directly corrupts the `initial_investment_min_usd` column used by the advisor's `$200 cap` filter — opportunities costing $1,500 would pass the filter incorrectly.

## Findings

- Proposed code: `nums = re.findall(r'\d[\d,]*\.?\d*', raw.replace(',', ''))`
- `raw.replace(',', '')` strips ALL commas from the entire string FIRST
- `"$1,500-$2,000"` → `"$15002000"` → regex matches `"15002000"` → result: `(15002000.0, 15002000.0)`
- The advisor query `WHERE initial_investment_min_usd <= 200` would pass opportunities costing $15M
- Review source: Kieran Python Reviewer (P1-3)

## Proposed Solutions

### Option 1: Strip commas only from matched tokens, not the full string

**Approach:**
```python
def parse_investment_range(raw: str) -> tuple[float | None, float | None]:
    nums = re.findall(r'\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+', raw)
    if not nums:
        return (None, None)
    vals = [float(n.replace('$', '').replace(',', '')) for n in nums]
    return (min(vals), max(vals))
```

**Pros:**
- Correct for all formats: "$500", "$1,500", "$1,500-$2,000", "500-1000", "~$2k"
- Simple one-function fix

**Cons:**
- Still misses shorthand like "$2k" (would need additional pattern)

**Effort:** 30 minutes

**Risk:** Low

---

### Option 2: Parse only min value (simplicity)

**Approach:** Extract first number only for `initial_investment_min_usd`. Drop `initial_investment_max_usd` column entirely (no consumer in week-1 plan).

**Pros:**
- Simpler regex, fewer edge cases
- Removes unused `max_usd` column

**Cons:**
- Less information stored

**Effort:** 20 minutes

**Risk:** Low

---

## Recommended Action

To be filled during triage.

## Technical Details

**Affected files:**
- `production_opportunity_pipeline.py` — proposed helper function (not yet implemented)
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — fix plan lines 296-303

**Database impact:**
- `initial_investment_min_usd NUMERIC(12,2)` — values would be wrong for any scraped opportunity with thousands separators

## Resources

- **Plan:** lines 296-303 (parse_investment_range pseudocode)
- **Review source:** Kieran Python Reviewer (P1-3)

## Acceptance Criteria

- [ ] `parse_investment_range("$1,500-$2,000")` → `(1500.0, 2000.0)`
- [ ] `parse_investment_range("$500-1000")` → `(500.0, 1000.0)`
- [ ] `parse_investment_range("under $200")` → `(None, 200.0)` or similar reasonable result
- [ ] `parse_investment_range("no investment needed")` → `(None, None)`
- [ ] Advisor query `WHERE initial_investment_min_usd <= 200` returns only genuinely low-cost opportunities

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)

**Actions:**
- Traced `raw.replace(',', '')` pre-processing bug
- Confirmed the wrong result for `"$1,500-$2,000"` format
- Identified impact on advisor $200 cap filter
