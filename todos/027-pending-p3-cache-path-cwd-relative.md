---
status: pending
priority: p3
issue_id: "027"
tags: [code-review, python, deployment, path]
dependencies: []
---

# CACHE_PATH in llm_cache.py is CWD-relative — breaks if launched from different directory

## Problem Statement

`CACHE_PATH = Path('data/llm_cache.sqlite')` resolves against the current working directory at runtime. If the systemd service runs with a different `WorkingDirectory` from where `data/` exists, the cache is created in the wrong location. Other data paths in the project use `Path(__file__).parent` or `WORKSPACE` constants — `CACHE_PATH` should be consistent.

## Findings

- Plan line 515: `CACHE_PATH = Path('data/llm_cache.sqlite')`
- `scrapers/config.py` uses `CACHE_DIR = Path(__file__).parent.parent / 'data' / 'cache'` — consistent with `__file__`
- systemd `WorkingDirectory=/opt/opportunity-research-bot` may not be where `data/` lives
- Review source: Kieran Python Reviewer (P3-17)

## Proposed Solutions

### Option 1: Use __file__-relative path

```python
CACHE_PATH = Path(__file__).parent.parent / 'data' / 'llm_cache.sqlite'
```

**Effort:** 5 minutes

**Risk:** None

## Acceptance Criteria

- [ ] `CACHE_PATH` is resolved relative to `llm_cache.py`'s location, not CWD
- [ ] Cache file is created in `<project_root>/data/llm_cache.sqlite` regardless of launch directory

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
