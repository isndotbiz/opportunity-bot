---
status: pending
priority: p3
issue_id: "028"
tags: [code-review, python, encoding, windows]
dependencies: []
---

# FICOParser.save_profile() and load_profile() open files without encoding='utf-8'

## Problem Statement

The plan correctly notes that `load_from_assessment_doc()` needs `encoding='utf-8'` to avoid Windows cp1252 issues. But `FICOParser.save_profile()` (line 244) and `FICOParser.load_profile()` (line 250) in the existing `fico_parser.py` both use `open(filepath, 'w')` and `open(filepath, 'r')` without explicit encoding. On Windows, these use cp1252 by default, causing `UnicodeEncodeError` or `UnicodeDecodeError` when business names contain non-ASCII characters.

## Findings

- `fico_parser.py:244`: `open(filepath, 'w')` — no encoding
- `fico_parser.py:250`: `open(filepath, 'r')` — no encoding
- Plan notes encoding issue only for the new `credit_data_ingestion.py`, not existing methods
- Business names with accented characters (e.g., "Société", "Müller LLC") would fail on Windows
- Review source: Kieran Python Reviewer (P3-18)

## Proposed Solutions

### Option 1: Add encoding='utf-8' to both calls

```python
# save_profile:
with open(filepath, 'w', encoding='utf-8') as f:

# load_profile:
with open(filepath, 'r', encoding='utf-8') as f:
```

**Effort:** 5 minutes

**Risk:** None — UTF-8 is the correct encoding for JSON files

## Acceptance Criteria

- [ ] `FICOParser.save_profile()` uses `encoding='utf-8'`
- [ ] `FICOParser.load_profile()` uses `encoding='utf-8'`
- [ ] A profile with non-ASCII characters in the business name round-trips correctly

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
