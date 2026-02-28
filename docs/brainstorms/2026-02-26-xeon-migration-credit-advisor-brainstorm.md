---
date: 2026-02-26
topic: xeon-migration-credit-advisor
---

# Xeon Migration, No-Auth Reddit, and Credit Advisor

## What We're Building

Three interconnected workstreams that transform the opportunity bot from a local research tool into an **autonomous Xeon-based agent** that scrapes 24/7, evaluates opportunities with Qwen3-30B-A3B, and surfaces the best candidate for a deployable micro-service.

**The north star:** The Xeon runs continuously. Scrapers feed Qwen3. The system flags the highest-scoring opportunity that fits the $200 budget constraint. A human reviews and deploys it as a pay-per-use API, subscription service, or one-time tool sale — targeting $5+ income in week 1.

> **Scope constraint:** "Autonomous build and deploy" means flag-for-human-deployment, not self-modifying or self-publishing code. The agent identifies; the human executes the first deploy.

---

## Workstream Sequencing

Workstreams are **not parallel-equal**:

1. **Workstream 1 (pgvector)** must complete first — all other workstreams write to or read from the database.
2. **Workstream 2 (Reddit scraper)** can proceed once Workstream 1 is running.
3. **Workstream 3 (credit advisor)** depends on Workstream 1 (pgvector schema) but not on Workstream 2.

---

## Workstream 1: ChromaDB → pgvector Migration

### Decision: Full migration to PostgreSQL + pgvector on Xeon

ChromaDB is replaced entirely. PostgreSQL + pgvector runs on the Xeon alongside the scrapers and LLM, giving a single database for structured metadata and vector embeddings.

**Why:** The user is moving the entire pipeline to the Xeon (scrapers, LLM, deployment). Running ChromaDB as a separate service adds no value when pgvector gives richer SQL filtering (scores, dates, sources) and integrates cleanly with agent tooling.

### Key Decisions
- **Collection name change:** `business_opportunities` table in PostgreSQL (replaces ChromaDB collection)
- **`config_chromadb.py` replaced** with a `config_db.py` that returns a pgvector-enabled PostgreSQL connection
- **`personalization_engine.py`** updated to use `config_db.py` (currently hardcoded to local ChromaDB path)
- **LLM:** Qwen3-30B-A3B @ 3.0bpw (already downloading to Xeon)
- **Architecture:** Everything on 10.0.0.87 — scraping, inference, pgvector, deployment

### Files to Change
- `config_chromadb.py` → replaced by `config_db.py`
- `production_opportunity_pipeline.py` — swap ChromaDB client for pgvector
- `query_opportunities.py` — swap ChromaDB queries for SQL + pgvector similarity search
- `credit_integration/personalization_engine.py` — use `config_db.py`
- `list_automation_opportunities.py` — fix stale collection name bug (uses old `"opportunities"`)

---

## Workstream 2: No-Auth Reddit Scraper

### Decision: Reddit public JSON API (no credentials needed)

The existing `RedditScraper` uses PRAW (requires OAuth credentials). Replace it with Reddit's public JSON API endpoints — `https://reddit.com/r/{subreddit}/new.json?limit=100` — which only require a User-Agent header.

**Why:** Simpler, no API key management, works immediately, covers the same subreddits. pushshift.io is shut down; snscrape's Reddit support is deprecated. The public JSON API is the most reliable no-auth path.

### Key Decisions
- **New file:** `scrapers/reddit_public_scraper.py` — replaces `scrapers/reddit_scraper.py` in the pipeline
- **User-Agent:** `OpportunityBot/2.0 (by /u/<your_username>)` — required by Reddit API TOS
- **Rate limiting:** 1 req/sec (Reddit's unauthenticated limit); at 20 subreddits this is ~20 seconds per full cycle — acceptable for a continuous background process
- **Wire into pipeline:** Update `production_opportunity_pipeline.py` to call the new scraper; current PRAW-based scraper is instantiated but gated on credentials
- **Subreddits:** Pull target list from `scrapers/config.py` (already defined there)

---

## Workstream 3: Credit Data Ingestion + Business Advisor

### Decision: Multi-source credit ingestion → risk profile + advisor output

The existing `fico_parser.py` has only Equifax business data hardcoded (Delinquency Score 372 → CONSERVATIVE). Personal FICO 763-788 and SBSS 210 are not wired in. This workstream fixes that and adds a credit advisor that gives actionable next steps.

**Credit profile source of truth:** `CREDIT_ASSESSMENT_2026-02-04.md`. Key facts: Personal FICO 763-788 (Very Good), SBSS 210/300 (passes SBA 7(a) threshold), business tradelines $137 total / fully utilized, Experian Business underdeveloped.

### Data Ingestion Approach

**Interim (start here):** Parse `CREDIT_ASSESSMENT_2026-02-04.md` directly — no credentials needed, unblocks all downstream advisor logic.

**Future:** Automate pulls from myFICO, Nav, and D&B. The mechanism for myFICO is an open question (no public API — browser automation or CSV export parsing are the options).

### Advisor Scope (Two Distinct Components)

**Component A — Risk Profile (`fico_parser.py` rewrite):**
- Ingest personal FICO alongside business scores
- Override CONSERVATIVE label when personal FICO >= 720 (unlocks MODERATE tier)
- Expose a structured risk profile object consumed by the opportunity filter

**Component B — Advisor Output (`credit_integration/advisor.py`):**
- **Immediate:** Opportunities executable now under $200 (hard cap)
- **Short-term (30–90 days):** Business credit building steps (fix Experian blank fields, add tradelines, reach $500+ credit limit)
- **Fund & Grow:** Flag 0% business credit card strategy; FICO 788 qualifies
- **SBA eligibility:** SBSS 210 passes threshold — surface SBA 7(a) / Microloan opportunities

The advisor does not become a general financial planning tool. It filters and annotates opportunities already in the database.

### Key Decisions
- **`fico_parser.py`:** Rewire to accept personal FICO scores; remove hardcoded Equifax-only data
- **Risk profile logic:** Personal FICO 788 overrides business Delinquency Score 372 for opportunity filtering (personal credit is the actual funding lever here)
- **New module:** `credit_integration/credit_data_ingestion.py` — starts with markdown parse, wires to live sources later
- **New module:** `credit_integration/advisor.py` — generates actionable advice from full profile
- **Opportunity filter hard cap:** $200 for "immediate" tier; higher tiers flagged but not default

---

## Resolved Questions

- **Xeon PostgreSQL:** Already running — needs `CREATE EXTENSION pgvector` and schema setup
- **Micro-service deployment:** Xeon builds the artifact → human pushes to Railway/Fly.io for public customer access
- **Reddit subreddits:** Use existing list already defined in `scrapers/config.py`
- **PRAW vs. public API:** Public JSON API replaces PRAW; no dual-mode needed

## Open Questions

- What OS is the Xeon running? (determines pgvector extension install path)
- What are the available credentials for myFICO, Nav, D&B? (gates the live ingestion phase of Workstream 3)
- Does the Xeon have sufficient VRAM to run Qwen3-30B-A3B @ 3.0bpw alongside PostgreSQL and active scrapers simultaneously? (If constrained, scraping and inference may need to run in alternating phases)
- What is the first specific micro-service to target for week-1 income? (This is the planning question — needs a decision before deployment, not before implementation of the three workstreams)

---

## Next Steps

→ `/workflows:plan` for implementation details on each workstream
