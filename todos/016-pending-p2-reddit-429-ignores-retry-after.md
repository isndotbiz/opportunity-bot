---
status: pending
priority: p2
issue_id: "016"
tags: [code-review, python, scrapers, reddit, error-handling]
dependencies: []
---

# Reddit 429 handler ignores Retry-After header and returns None silently on second failure

## Problem Statement

The proposed `RedditPublicScraper._get()` handles HTTP 429 by sleeping 60 seconds and retrying once. But Reddit's 429 response includes a `Retry-After` header specifying the exact backoff. Ignoring it means the scraper either under-waits (if Reddit says 120s) or over-waits (if it says 10s). More critically, a second 429 returns `None` with no logging, silently dropping that subreddit from the run.

## Findings

- Proposed code: `if resp.status_code == 429: time.sleep(60); resp = self.session.get(url, timeout=10)`
- Reddit's 429 includes `Retry-After: <seconds>` header
- After second 429: `if resp.status_code != 200: return None` — no logging, no metric
- `except Exception: return None` is equally silent on network errors
- Plan's error propagation doc says "log and skip that subreddit on second failure" — but the code doesn't log
- Review source: Kieran Python Reviewer (P2-12)

## Proposed Solutions

### Option 1: Use Retry-After header with logging

```python
def _get(self, url: str) -> dict | None:
    for attempt in range(2):
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                wait = int(resp.headers.get('Retry-After', 60))
                logger.warning(f"Reddit 429 on {url}, waiting {wait}s (attempt {attempt+1}/2)")
                time.sleep(wait)
                continue
            logger.warning(f"Reddit non-200 ({resp.status_code}) on {url}")
            return None
        except Exception as e:
            logger.error(f"Reddit request error on {url}: {e}")
            return None
    logger.error(f"Reddit 429 persists after retry, skipping: {url}")
    return None
```

**Effort:** 30 minutes

**Risk:** Low

---

## Technical Details

**Affected files:**
- `scrapers/reddit_public_scraper.py` (new file per plan) — `_get()` method

## Acceptance Criteria

- [ ] `Retry-After` header is read and used when present
- [ ] Both 429 failures and network errors are logged with the URL
- [ ] Skipped subreddits are logged at ERROR level
- [ ] Second 429 does not silently return None without a log entry

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
