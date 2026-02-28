---
status: pending
priority: p3
issue_id: "029"
tags: [code-review, security, prompt-injection, llm]
dependencies: []
---

# Prompt injection truncation incomplete — tech_stack and source fields not covered

## Problem Statement

The plan proposes truncating `title` (200 chars), `description` (500 chars), and `revenue_claim` (100 chars) before LLM interpolation. But the LLM prompt in `production_opportunity_pipeline.py` also directly interpolates `tech_stack` and `source`, which are NOT truncated. A scraped post could include a prompt injection in `tech_stack` that bypasses the truncation defenses. The `validate_analysis()` function also doesn't validate `key_insights` and `risks` as bounded arrays.

## Findings

- Plan truncation covers: `title`, `description`, `revenue_claim`
- NOT covered: `tech_stack`, `source` (both directly interpolated into LLM prompt per line 128-153)
- `source` is constructed from scraper metadata, less directly attacker-controlled but still injectable
- `validate_analysis()` validates `automation_score`, `legitimacy_score`, `recommended_action` — NOT `key_insights` (TEXT[]) or `risks` (TEXT[])
- Malformed `key_insights` array could store attacker-controlled text in the database
- Review source: Security Sentinel (P3-A)

## Proposed Solutions

### Option 1: Add truncation for all interpolated fields

```python
# Add to the sanitization block:
opportunity['tech_stack'] = opportunity.get('tech_stack', '')[:200]
opportunity['source'] = opportunity.get('source', '')[:100]

# Add to validate_analysis():
def validate_analysis(analysis: dict) -> bool:
    ...
    # Validate arrays
    for field in ['key_insights', 'risks']:
        val = analysis.get(field, [])
        if not isinstance(val, list):
            return False
        if len(val) > 10:
            analysis[field] = val[:10]  # truncate to 10 items
        analysis[field] = [str(item)[:500] for item in val]  # truncate each item
    return True
```

**Effort:** 30 minutes

**Risk:** Low

## Acceptance Criteria

- [ ] `tech_stack` and `source` are truncated before LLM interpolation
- [ ] `validate_analysis()` validates and truncates `key_insights` and `risks` arrays
- [ ] Each array element is bounded to a reasonable length (e.g., 500 chars)
- [ ] Array length is bounded (e.g., max 10 items)

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
