---
status: pending
priority: p2
issue_id: "018"
tags: [code-review, security, python, path-traversal]
dependencies: []
---

# load_from_assessment_doc() reads file by path without canonicalization — path traversal risk

## Problem Statement

The proposed `load_from_assessment_doc(path: Path)` function accepts an arbitrary `Path` object and reads it without canonicalization or bounds checking. The caller in `personalized_opportunity_bot.py` uses a relative path `Path('CREDIT_ASSESSMENT_2026-02-04.md')` which resolves against the current working directory — incorrect if the systemd service runs from a different `WorkingDirectory`. If the function is ever exposed to external input (e.g., a CLI flag `--assessment-file`), it allows reading any file on the system.

## Findings

- Proposed caller: `assessment_path = Path('CREDIT_ASSESSMENT_2026-02-04.md')` — CWD-relative
- systemd `WorkingDirectory=/opt/opportunity-research-bot` may differ from where the file is actually placed
- No `path.resolve()` → no canonicalization
- No bounds check: function accepts `Path('/etc/passwd')` without complaint
- `FileNotFoundError` message includes the full filesystem path — information leakage
- Review source: Security Sentinel (P2-C)

## Proposed Solutions

### Option 1: Use __file__-relative path in caller, add bounds check in function

```python
# In personalized_opportunity_bot.py:
ASSESSMENT_PATH = Path(__file__).parent / 'CREDIT_ASSESSMENT_2026-02-04.md'

# In credit_data_ingestion.py:
def load_from_assessment_doc(path: Path) -> CreditProfile:
    resolved = path.resolve()
    project_root = Path(__file__).parent.parent.resolve()
    if not str(resolved).startswith(str(project_root)):
        raise ValueError(f"Assessment path must be within project directory")
    if not resolved.exists():
        raise FileNotFoundError(f"Assessment document not found (check CLAUDE.md for expected location)")
    text = resolved.read_text(encoding='utf-8')
    ...
```

**Effort:** 30 minutes

**Risk:** Low

---

## Technical Details

**Affected files:**
- `credit_integration/credit_data_ingestion.py` (new file) — `load_from_assessment_doc()`
- `personalized_opportunity_bot.py` — caller using `Path('CREDIT_ASSESSMENT_2026-02-04.md')`

## Acceptance Criteria

- [ ] Default path is resolved relative to `__file__`, not CWD
- [ ] `load_from_assessment_doc()` validates the resolved path is within the project directory
- [ ] Error message does not include the full filesystem path on failure

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
