---
status: pending
priority: p3
issue_id: "030"
tags: [code-review, scrapers, reddit, tos-compliance]
dependencies: []
---

# Reddit User-Agent has (by /u/unknown) placeholder default — ToS violation in production

## Problem Statement

The plan's `scrapers/config.py` proposal sets `REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'python:com.isnbiz.opportunitybot:v2.0 (by /u/unknown)')`. The fallback `(by /u/unknown)` is a Reddit ToS violation — Reddit requires a real account username for contact purposes. If the env var is not set, the scraper will use the placeholder default and risk IP bans for the Xeon server.

## Findings

- Reddit API rules: User-Agent must include `(by /u/<real_username>)` for accountability
- `(by /u/unknown)` and `(by /u/YOUR_REDDIT_USERNAME)` are concrete non-compliant values
- If the env var is unset (common in fresh deployments), the default reaches Reddit's servers
- Current production code already uses `"OpportunityBot/1.0"` with no username at all (also non-compliant)
- Review source: Security Sentinel (P3-B)

## Proposed Solutions

### Option 1: Fail loudly if REDDIT_USER_AGENT is not set

```python
# In RedditPublicScraper.__init__():
user_agent = os.environ.get('REDDIT_USER_AGENT')
if not user_agent or '/u/' not in user_agent:
    raise ValueError(
        "REDDIT_USER_AGENT env var must be set and include '(by /u/<your_username>)'. "
        "Example: 'python:com.isnbiz.opportunitybot:v2.0 (by /u/jdmal)'"
    )
self.session.headers.update({'User-Agent': user_agent})
```

**Pros:**
- Fails loudly at startup rather than silently using a bad User-Agent
- No fallback default that could reach Reddit's servers

**Effort:** 15 minutes

**Risk:** Low

## Acceptance Criteria

- [ ] No default fallback for `REDDIT_USER_AGENT` that contains placeholder text
- [ ] `RedditPublicScraper` raises `ValueError` at startup if `REDDIT_USER_AGENT` is not set or invalid
- [ ] `.env.tpl` includes `REDDIT_USER_AGENT=python:com.isnbiz.opportunitybot:v2.0 (by /u/<YOUR_REDDIT_USERNAME>)` with a clear placeholder

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
