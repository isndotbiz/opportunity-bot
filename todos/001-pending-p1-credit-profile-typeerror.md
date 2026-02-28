---
status: pending
priority: p1
issue_id: "001"
tags: [code-review, python, data-model, credit-integration]
dependencies: []
---

# CreditProfile constructor TypeError in load_from_assessment_doc()

## Problem Statement

`credit_data_ingestion.py`'s proposed `load_from_assessment_doc()` will raise `TypeError` on first run. The function passes non-existent keyword arguments (`credit_limit`, `derogatory_marks`, `sbss_score`) and omits a required positional argument (`business_type`). The pipeline will crash immediately when trying to build the credit profile from the markdown assessment doc.

## Findings

- Plan's proposed `CreditProfile(credit_limit=137, derogatory_marks=0, sbss_score=210)` — none of these fields exist in the actual `CreditProfile` dataclass in `credit_integration/fico_parser.py`
- Actual dataclass fields: `total_credit_limit`, `total_balance`, `available_credit`, `current_accounts`, `delinquent_accounts`, `total_tradelines`, `bankruptcies`, `judgments`, `liens`
- `business_type: BusinessType` has no default value in the dataclass — omitting it raises `TypeError: __init__() missing 1 required positional argument: 'business_type'`
- `years_in_business=2.0` (float) vs field annotation `Optional[int]` — type mismatch (silent, but prints "2.0 years" not "2 years")
- Source: Kieran Python Reviewer finding P1-1 and P1-14

## Proposed Solutions

### Option 1: Fix the constructor call to use correct field names

**Approach:** Update the proposed `CreditProfile(...)` call in `load_from_assessment_doc()` to use actual dataclass field names and add `business_type=BusinessType.C_CORP`.

**Pros:**
- Minimal change, preserves existing dataclass
- Correct fix — uses the fields that actually exist

**Cons:**
- `sbss_score` has nowhere to go (not in dataclass) — needs a new field or a wrapper object

**Effort:** 1 hour

**Risk:** Low

---

### Option 2: Add missing fields to CreditProfile dataclass

**Approach:** Add `sbss_score: Optional[int] = None`, `derogatory_marks: Optional[int] = None`, and `business_type: BusinessType = BusinessType.C_CORP` (with default) to the dataclass before `load_from_assessment_doc()` is implemented.

**Pros:**
- More complete credit profile object
- Enables future SBSS-based filtering

**Cons:**
- Requires updating `to_dict()`, `from_dict()`, and all test fixtures
- Cascading changes

**Effort:** 2-3 hours

**Risk:** Medium — touches existing serialization

---

## Recommended Action

To be filled during triage.

## Technical Details

**Affected files:**
- `credit_integration/fico_parser.py` — `CreditProfile` dataclass definition
- `credit_integration/credit_data_ingestion.py` (new file per plan) — `load_from_assessment_doc()`
- `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` — plan must be corrected before implementation

**Related components:**
- `personalized_opportunity_bot.py` — calls `_load_or_create_profile()` which calls `load_from_assessment_doc()`

## Resources

- **Plan:** `docs/plans/2026-02-26-feat-xeon-pgvector-reddit-credit-advisor-plan.md` lines 767-777 (proposed constructor call)
- **Actual dataclass:** `credit_integration/fico_parser.py` CreditProfile definition
- **Review source:** Kieran Python Reviewer (P1-1, P1-14)

## Acceptance Criteria

- [ ] `load_from_assessment_doc()` uses only field names that exist in `CreditProfile`
- [ ] `business_type` argument is provided (either as default in dataclass or explicit in call)
- [ ] `years_in_business` is an integer, not float
- [ ] `sbss_score` has a home (new dataclass field or separate attribute)
- [ ] Manual test: `load_from_assessment_doc(Path('CREDIT_ASSESSMENT_2026-02-04.md'))` runs without TypeError

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)

**Actions:**
- Identified mismatch between plan's proposed constructor call and actual CreditProfile dataclass
- Confirmed `business_type` has no default value — constructor call will raise TypeError
- Confirmed `credit_limit`, `derogatory_marks`, `sbss_score` are not dataclass fields
