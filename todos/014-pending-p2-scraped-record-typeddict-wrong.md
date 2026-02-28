---
status: pending
priority: p2
issue_id: "014"
tags: [code-review, python, scrapers, type-safety]
dependencies: []
---

# ScrapedRecord TypedDict omits `tags` field and spuriously includes `score`

## Problem Statement

The proposed `ScrapedRecord` TypedDict has 8 fields: title, description, source, url, score, created, revenue_claim, tech_stack. But actual scrapers (HackerNews, ProductHunt) emit a `tags` field that is absent from the TypedDict, and `score` (Reddit upvote count) is not produced by HN or PH scrapers. If `ScrapedRecord` is used as the common record type for all scrapers (per acceptance criteria), the contract is wrong.

## Findings

- `hackernews_scraper.py` produces `tags` key; `ScrapedRecord` has no `tags` field
- `producthunt_scraper.py` produces `tags` key; `ScrapedRecord` has no `tags` field
- `score` is Reddit-specific (upvotes); HN and PH have no equivalent
- Plan acceptance criteria: "All scrapers produce `ScrapedRecord` TypedDict"
- Python TypedDicts are not enforced at runtime — this creates a misleading contract without errors
- Review source: Kieran Python Reviewer (P2-7)

## Proposed Solutions

### Option 1: Add tags to TypedDict, make score Optional

```python
class ScrapedRecord(TypedDict, total=False):
    title: str
    description: str
    source: str
    url: str
    score: int          # Optional: Reddit upvotes; absent for HN/PH
    created: str
    revenue_claim: str
    tech_stack: str
    tags: list[str]     # Optional: HN/PH categories; absent for Reddit

# Required fields only:
class ScrapedRecord(TypedDict):
    title: str
    description: str
    source: str
    url: str
    created: str
```

**Effort:** 30 minutes

**Risk:** Low

---

### Option 2: Source-specific TypedDicts inheriting from base

**Approach:** `BaseRecord` with common fields; `RedditRecord(BaseRecord)` adds `score`; `HNRecord(BaseRecord)` adds `tags`.

**Effort:** 1 hour

**Risk:** Low

---

## Technical Details

**Affected files:**
- `production_opportunity_pipeline.py` — proposed `ScrapedRecord` TypedDict
- `scrapers/hackernews_scraper.py` — emits `tags` field
- `scrapers/producthunt_scraper.py` — emits `tags` field

## Acceptance Criteria

- [ ] `ScrapedRecord` includes `tags: list[str]` as Optional or in base TypedDict
- [ ] `score` is Optional or removed from base TypedDict
- [ ] All scrapers produce records compatible with the TypedDict contract
- [ ] The pipeline handles missing `score`/`tags` gracefully

## Work Log

### 2026-02-26 - Code Review Discovery

**By:** Claude Code (workflows:review)
