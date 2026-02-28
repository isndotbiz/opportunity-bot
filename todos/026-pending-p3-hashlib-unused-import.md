---
status: pending
priority: p3
issue_id: "026"
tags: [code-review, python, cleanup]
dependencies: []
---

# import hashlib unused in make_doc_id code block

## Problem Statement

The plan's proposed `make_doc_id()` function imports `hashlib` but never uses it — the implementation uses `uuid.uuid5()` instead. This is a leftover from the previous sha256-based `doc_id` approach that was superseded in Round 2.

## Findings

- Plan lines 280-285: `import uuid; import hashlib` then `return str(uuid.uuid5(uuid.NAMESPACE_URL, url))`
- `hashlib` is imported but not called anywhere in the code block
- Likely leftover from Round 1's sha256 approach
- Review source: Kieran Python Reviewer (P3-16)

## Proposed Solutions

### Option 1: Remove the unused import

Remove `import hashlib` from the `make_doc_id()` code block.

**Effort:** 2 minutes

**Risk:** None

## Acceptance Criteria

- [ ] `import hashlib` is not present in `make_doc_id()` implementation
- [ ] `ruff check` or `flake8` reports no F401 (unused import) for this module

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
