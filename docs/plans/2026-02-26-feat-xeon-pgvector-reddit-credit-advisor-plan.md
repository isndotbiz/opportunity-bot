---
title: "feat: Xeon pgvector migration, no-auth Reddit scraper, and credit advisor"
type: feat
status: active
date: 2026-02-26
origin: docs/brainstorms/2026-02-26-xeon-migration-credit-advisor-brainstorm.md
---

# feat: Xeon pgvector migration, no-auth Reddit scraper, and credit advisor

## Enhancement Summary (Second Deepening)

**Deepened on:** 2026-02-26 (Round 2)
**Round 2 agents:** schema-drift-detector, kieran-python-reviewer (2nd pass), architecture-strategist (2nd pass), performance-oracle (2nd pass), security-sentinel (2nd pass), data-integrity-guardian (2nd pass), code-simplicity-reviewer (2nd pass), framework-docs-researcher, best-practices-researcher, git-history-analyzer, pattern-recognition-specialist, deployment-verification-agent (2nd pass), agent-native-architecture skill, orchestrating-swarms skill, pgvector web research, Xeon architecture research

### Key Improvements Added in Round 2

1. **CRITICAL SECURITY — `test_isnbiz.json` already committed**: `credit_integration/profiles/test_isnbiz.json` is tracked in git commit `4558a05` with Equifax business ID 722429197, credit score 372, and full tradeline data. `credit_integration/profiles/` is NOT in `.gitignore`. Must be purged from git history.
2. **Schema drift — `scalability_score` semantic mismatch**: LLM prompt asks for `"scalability": <1-5>` but DDL defines `scalability_score INTEGER CHECK (BETWEEN 0 AND 100)`. These are incompatible — must pick one and align all three sources (DDL, LLM prompt, `models.py`).
3. **`recommended_action` silently dropped**: The field was removed from the DDL without acknowledgement. It exists in the LLM output and fallback analysis and must either be mapped to a column or explicitly dropped from the prompt.
4. **Investment range storage**: `"$500-1000"` → `initial_investment_min_usd` + `initial_investment_max_usd` (two columns). Single column stores wrong value for advisor filtering.
5. **`embedding_status` tracking column**: `NULL` embedding is ambiguous between "never attempted" and "attempted and failed". Add `embedding_status TEXT` column with values `pending/processing/complete/failed/skipped`.
6. **Context manager pattern**: `get_pgvector_client()` must become `get_pgvector_connection()` as a `@contextmanager`. Raw psycopg2 connections must have explicit ownership contracts or connections leak.
7. **`create_schema()` wrong home**: DDL that runs once belongs in `scripts/setup_pgvector.py` or `schema.sql`, not in `config_db.py` which is imported every run.
8. **`query_by_similarity()` premature abstraction**: Three callers need different WHERE clauses, different columns, different ORDER BY — the shared function would require 5+ optional parameters. Remove it; each caller writes its own SQL.
9. **`embeddings.py` singleton module**: Three callers (pipeline, advisor, query CLI) each need the embedding model. Lazy singleton in a dedicated module prevents 3x memory use and avoids import-time load.
10. **`create_isnbiz_profile()` removal requires replacement**: This method is actively called in `personalized_opportunity_bot.py` production logic (not just demos). Removing it breaks the bootstrapping flow. A replacement `load_or_create_profile()` is needed.
11. **LLM result caching is #1 performance win**: Daily re-scrape of the same URLs triggers full re-analysis. SQLite cache keyed on `sha256(url)` achieves ~90% cache hit rate, reducing 112-minute analysis to ~11 minutes.
12. **`<#>` operator + `hnsw.iterative_scan`**: Pre-normalized vectors should use negative inner product (`<#>`) instead of cosine (`<=>`). For filtered queries, enable `SET hnsw.iterative_scan = relaxed_order` (pgvector 0.8.0+).
13. **Xeon always-on architecture**: systemd service + asyncio producer/consumer + Redis seen-URL dedup for the production continuous pipeline. Replaces cron-fired one-shot script.
14. **`time_mentioned` removed from `ScrapedRecord`**: Field is always "Not specified", not in pgvector schema, serves no purpose. Remove from TypedDict.
15. **ProductHunt O(n²) URL dedup bug**: `if url not in [p.get('url') for p in products]` creates a new list and scans it linearly on every iteration. Replace with `seen_urls = set()`.

### New Corrections to Previous Pass

- `config_chromadb.py` was **never committed** — rollback step `git checkout HEAD -- config_chromadb.py` will fail; it does not exist in git history
- `credit_scorer.py` returns `@dataclass` (`MatchScore`), not plain dict — previous plan's "use plain dict" recommendation was incorrect for the domain; advisor should use `@dataclass` or explicitly convert
- `list_automation_opportunities.py` uses three wrong field names beyond the stale collection name: `revenue_potential` (should be `revenue_claim`), `investment_required` (not stored), `source_url` (should be `url`)
- `HackerNewsScraper` and `ProductHuntScraper` are NOT in `scrapers/__init__.py` — must be added
- Reddit authenticated rate limit is 60 req/min (via PRAW OAuth), not 10 req/min (unauthenticated only)
- SBSS threshold formally sunset March 1, 2026; lender practical floor is 175-180; use 155 as eligibility gate since SBSS 210 clears all thresholds

---

## Enhancement Summary (First Deepening)

**Deepened on:** 2026-02-26 (Round 1)
**Round 1 agents:** architecture-strategist, kieran-python-reviewer, data-integrity-guardian, performance-oracle, security-sentinel, best-practices-researcher, framework-docs-researcher, code-simplicity-reviewer, deployment-verification-agent, data-migration-expert, agent-native-reviewer, pattern-recognition-specialist

### Key Improvements (Round 1)

1. **CRITICAL SECURITY**: `CREDIT_ASSESSMENT_2026-02-04.md` contains personal PII committed to git. Verify/purge before any other work.
2. **`register_vector()` is per-connection** — must be called inside the connection factory after each `connect()`.
3. **Reddit rate limit corrected** — 10 req/min unauthenticated = 6 seconds between requests.
4. **Schema hardened** — `NOT NULL`/`CHECK` constraints, partial HNSW index, `m=32, ef_construction=128`.
5. **Batch embeddings** — instantiate `SentenceTransformer` once; encode all docs before INSERT.
6. **Simplifications** — removed `personal_fico_available: bool`, `AdvisorReport` dataclass, separate `migrate_to_pgvector.py`, `CreditAdvisor` class.
7. **hashlib.sha256 doc_id** — replaces broken `hash(url) % 10000`.
8. **Agent-native output** — advisor writes `reports/advisor/latest.json`.

---

## Overview

Three sequenced workstreams that transform the opportunity bot into an autonomous Xeon-based agent: replace ChromaDB with PostgreSQL + pgvector, activate Reddit scraping without credentials, and wire in real credit profile data with tiered advisor output.

**North star:** Xeon scrapes 24/7 with Qwen3-30B-A3B, stores to pgvector, advisor surfaces the best opportunity under $200 to execute for $5+ income in week 1.

> **Scope:** "Deploy" means the human pushes to Railway/Fly.io after the agent flags a candidate. No autonomous code publishing.

---

## Workstream Sequencing

```
[W1: pgvector] ──── done ────┬──► [W2: Reddit scraper]
                              └──► [W3: Credit advisor]
```

W1 must complete first. W2 and W3 can proceed in parallel once W1 is running.

---

## 🚨 CRITICAL: Pre-Work Security Actions (Both Issues)

**Execute in order before implementing anything:**

### Issue 1: `test_isnbiz.json` committed to git history (commit 4558a05)

```bash
# Check what is committed
git show 4558a05:credit_integration/profiles/test_isnbiz.json

# Purge from git history
pip install git-filter-repo
git filter-repo --path credit_integration/profiles/ --invert-paths

# Add to .gitignore
echo "credit_integration/profiles/" >> .gitignore
echo "reports/" >> .gitignore
echo "reports/advisor/" >> .gitignore

# Commit the gitignore update
git add .gitignore && git commit -m "security: add profiles/ and reports/ to gitignore"

# Force push required (destructive — coordinate with any collaborators)
git push --force
```

### Issue 2: `CREDIT_ASSESSMENT_2026-02-04.md` in git

```bash
# Check if pushed to remote
git log --remotes --oneline -- CREDIT_ASSESSMENT_2026-02-04.md

# If in remote history:
git filter-repo --path CREDIT_ASSESSMENT_2026-02-04.md --invert-paths
echo "CREDIT_ASSESSMENT_*.md" >> .gitignore
```

### Issue 3: Prompt injection — add before next scrape run

In `production_opportunity_pipeline.py`, before building the LLM prompt, add field-level length limits:
```python
opportunity['title'] = opportunity.get('title', '')[:200]
opportunity['description'] = opportunity.get('description', '')[:500]
opportunity['revenue_claim'] = opportunity.get('revenue_claim', '')[:100]
```

After `json.loads(analysis_text)`, validate against expected ranges:
```python
def validate_analysis(analysis: dict) -> dict:
    analysis['automation_score'] = max(0, min(100, int(analysis.get('automation_score', 50))))
    analysis['legitimacy_score'] = max(0, min(100, int(analysis.get('legitimacy_score', 50))))
    valid_actions = {'high', 'medium', 'low'}
    if analysis.get('recommended_action', '').lower() not in valid_actions:
        analysis['recommended_action'] = 'medium'
    return analysis
```

### Additional Xeon security notes (out of scope but flagged)
- ChromaDB, Redis, Neo4j, Qdrant on Xeon have no authentication — plaintext HTTP on LAN
- LLM Docker may bind to `0.0.0.0`; confirm it is `127.0.0.1` only
- Product Hunt scraper uses fake browser User-Agent (ToS violation — use `OpportunityBot/2.0 (+contact@yourdomain.com)`)
- Reddit User-Agent must include `/u/yourusername` per Reddit API ToS
- `--no-verify` instruction must be removed from `CLAUDE.md`
- `credit_integration/profiles/` output should write to `~/.opportunity-bot/profiles/` (outside repo)

---

## Problem Statement

| Problem | Current State | Impact |
|---------|--------------|--------|
| ChromaDB client created per-document | N new clients per pipeline run; no connection reuse | Slow pipeline, no dedup on URL |
| Reddit scraper never called in production | Imported but not instantiated (replaced by HN/PH in uncommitted work) | Major scrape source silently inactive |
| Personal FICO 763-788 absent from system | Only Equifax Delinquency Score 372 used → CONSERVATIVE profile, $100 floor | Wrong risk tier; advisor unusable |
| `personalization_engine.py` bypasses `config_chromadb.py` | Line 88: hardcoded `chromadb.PersistentClient` at local path | Never queries Xeon ChromaDB — broken TODAY |
| `query_opportunities.py` reads fields not stored | Reads `time_to_market`, `initial_investment`, `tech_stack` — none stored by pipeline | KeyError on every result |
| `hash(url) % 10000` for doc_id | Non-deterministic; collision confirmed at 64 records | Silently drops or overwrites valid records |
| `list_automation_opportunities.py` uses 3 wrong field names | `revenue_potential`, `investment_required`, `source_url` — none match stored fields | Broken regardless of migration |
| LLM re-analyzes every URL on every run | No caching by URL hash | 112 min/run on CPU when 90% are seen URLs |

---

## Proposed Solution

### Workstream 1: ChromaDB → pgvector
Replace `config_chromadb.py` with `config_db.py` (context manager factory). Add `embeddings.py` singleton. Create `business_opportunities` table. Update all callers.

### Workstream 2: No-Auth Reddit Scraper
Create `scrapers/reddit_public_scraper.py` using Reddit public JSON API. Wire into pipeline.

### Workstream 3: Credit Data Ingestion + Advisor
Add `personal_fico_score` to `CreditProfile`. Write `credit_data_ingestion.py`. Write `advisor.py`. Write replacement bootstrapping for `personalized_opportunity_bot.py`.

---

## Technical Approach

### Architecture

```
[Xeon 10.0.0.87]
├── PostgreSQL + pgvector (opportunity_bot database)
├── Redis (seen-URL dedup cache, 6379)
├── Qwen3-30B-A3B @ 3.0bpw (CPU inference ~30-60s/opp)
└── Scrapers (Reddit, HN, PH, IH)

[systemd service: opportunity-bot.service]
└── Always-on pipeline daemon (asyncio producer/consumer + ProcessPoolExecutor)
    ├── Scraper tasks (async, I/O-bound)
    ├── LLM analyzer workers (subprocess, CPU/GPU-bound)
    └── Store worker (psycopg2 + pgvector)

[Local workstation]
├── query_opportunities.py → connects to Xeon Postgres
└── credit_integration/advisor.py → connects to Xeon Postgres
```

### Database Schema (DDL — corrected)

```sql
-- Run once via scripts/setup_pgvector.py (NOT inside config_db.py)
CREATE DATABASE opportunity_bot;
\c opportunity_bot

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS business_opportunities (
    id                      SERIAL PRIMARY KEY,
    doc_id                  TEXT UNIQUE NOT NULL,           -- uuid5(NAMESPACE_URL, url)
    title                   TEXT NOT NULL,
    description             TEXT,
    source                  TEXT NOT NULL,
    url                     TEXT NOT NULL UNIQUE,           -- two-layer dedup
    revenue_claim           TEXT,
    automation_score        INTEGER CHECK (automation_score BETWEEN 0 AND 100),
    legitimacy_score        INTEGER CHECK (legitimacy_score BETWEEN 0 AND 100),
    scalability_score       INTEGER CHECK (scalability_score BETWEEN 1 AND 5),   -- 1-5 scale (matches LLM prompt)
    technical_difficulty    INTEGER CHECK (technical_difficulty BETWEEN 1 AND 5),
    recommended_action      TEXT CHECK (recommended_action IN ('high', 'medium', 'low')),
    initial_investment      TEXT,                           -- free-text display ("$500-1000")
    initial_investment_min_usd NUMERIC(12,2),               -- lower bound, parsed at insert
    initial_investment_max_usd NUMERIC(12,2),               -- upper bound ("$500-1000" → max=1000)
    time_to_market          TEXT,
    tech_stack              TEXT,
    category                TEXT,
    key_insights            TEXT[] NOT NULL DEFAULT '{}',
    risks                   TEXT[] NOT NULL DEFAULT '{}',
    analysis_version        INTEGER NOT NULL DEFAULT 1,     -- INTEGER not TEXT (avoids '1.9' > '1.10')
    embedding_status        TEXT NOT NULL DEFAULT 'pending'
                               CHECK (embedding_status IN ('pending','processing','complete','failed','skipped')),
    embedding_error         TEXT,
    analyzed_at             TIMESTAMPTZ,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    embedding               vector(384)                     -- all-MiniLM-L6-v2, NULL until embedded
);

-- Partial HNSW index (only rows with embeddings; pre-normalized → use inner product)
CREATE INDEX IF NOT EXISTS opp_embedding_hnsw
    ON business_opportunities
    USING hnsw (embedding vector_ip_ops)                    -- <#> for pre-normalized vectors (faster than <=>)
    WITH (m = 32, ef_construction = 128)
    WHERE embedding IS NOT NULL;

-- Score-based filtering
CREATE INDEX IF NOT EXISTS opp_automation_score
    ON business_opportunities (automation_score DESC)
    WHERE automation_score IS NOT NULL;

-- Compound index for advisor $200 cap queries
CREATE INDEX IF NOT EXISTS opp_investment_automation
    ON business_opportunities (initial_investment_min_usd, automation_score DESC)
    WHERE initial_investment_min_usd IS NOT NULL;

-- Operational: embedding backfill
CREATE INDEX IF NOT EXISTS opp_embedding_status
    ON business_opportunities (embedding_status)
    WHERE embedding_status != 'complete';

-- Version-based re-analysis detection
CREATE INDEX IF NOT EXISTS opp_analysis_version
    ON business_opportunities (analysis_version)
    WHERE analysis_version < 2;                             -- update threshold as prompt versions change
```

**Schema decisions (Round 2 corrections):**
- `scalability_score CHECK (BETWEEN 1 AND 5)` — LLM prompt asks for 1-5 scale; DDL now matches prompt and `models.py` must be updated to `Field(ge=1, le=5)`
- `recommended_action TEXT CHECK (IN ('high','medium','low'))` — preserved from LLM output; use normalize_priority() before INSERT
- `initial_investment_min_usd` + `initial_investment_max_usd` — two columns because "$500-1000" has a meaningful upper bound for advisor filtering
- `key_insights TEXT[] NOT NULL DEFAULT '{}'` — `NOT NULL DEFAULT '{}'` prevents NULL/empty ambiguity
- `analysis_version INTEGER` — integer arithmetic works correctly (`< 2`); TEXT lexicographic ordering fails (`'1.9' > '1.10'`)
- `embedding_status` column — distinguishes "never attempted" from "failed" from "skipped" (description too long)
- `vector_ip_ops` — use inner product since we store pre-normalized unit vectors; mathematically equivalent to cosine but faster at query time
- `doc_id = uuid5(NAMESPACE_URL, url)` — standard, self-documenting, unambiguous (replaces truncated sha256 hex)

**Python coercions needed before every INSERT:**
```python
import uuid
import hashlib

def make_doc_id(url: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))

def normalize_priority(raw: str) -> str:
    norm = raw.strip().lower()
    return norm if norm in {'high', 'medium', 'low'} else 'medium'

def coerce_to_list(value) -> list[str]:
    if isinstance(value, list): return value
    if value is None: return []
    if isinstance(value, str): return [value] if value.strip() else []
    return []

def parse_investment_range(raw: str) -> tuple[float | None, float | None]:
    """Parse "$500-1000" → (500.0, 1000.0); "$200" → (200.0, 200.0)."""
    import re
    nums = re.findall(r'\d[\d,]*\.?\d*', raw.replace(',', ''))
    if not nums: return (None, None)
    vals = [float(n.replace(',', '')) for n in nums]
    return (min(vals), max(vals))
```

---

### New Module: `embeddings.py` (singleton)

Three callers need the embedding model: pipeline, advisor, query CLI. A singleton module prevents 3x memory load (~90MB each) and avoids import-time initialization:

```python
# embeddings.py — lazy singleton, not imported at module level
from __future__ import annotations
from sentence_transformers import SentenceTransformer
import numpy as np

_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model

def encode(texts: list[str], batch_size: int = 32) -> np.ndarray:
    """Encode texts to unit-length vectors (normalize_embeddings=True for <#> operator)."""
    return get_model().encode(texts, normalize_embeddings=True, batch_size=batch_size)
```

All callers replace `SentenceTransformer('all-MiniLM-L6-v2').encode(...)` with `from embeddings import encode`.

**Thread safety note:** Do not share the model across Python threads for concurrent `encode()` calls — GIL serializes them and tokenizer state can corrupt. One model instance per process is safe for sequential or asyncio-based pipelines.

---

### New File: `scripts/setup_pgvector.py` (replaces `create_schema()` in `config_db.py`)

DDL that runs once does not belong in a module imported every run. Move to a standalone script:

```bash
# Run once on Xeon before first pipeline run
python scripts/setup_pgvector.py
```

The script: connects, runs CREATE EXTENSION, CREATE TABLE, CREATE INDEX, prints confirmation, exits. No other logic.

---

### Implementation Phases

#### Phase 1: pgvector Foundation (W1)

**1.1 Create `config_db.py`**

Context manager factory — not a raw connection factory:

```python
from contextlib import contextmanager
from typing import Generator
import os
import psycopg2
import psycopg2.extensions
from pgvector.psycopg2 import register_vector

@contextmanager
def get_pgvector_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Context manager that opens a psycopg2 connection with pgvector registered.
    Commits on clean exit, rolls back on exception, always closes.

    Usage:
        with get_pgvector_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT ...")
    """
    conn = psycopg2.connect(
        host=os.environ['PG_HOST'],         # KeyError if missing — loud failure beats silent wrong value
        port=int(os.environ.get('PG_PORT', '5432')),
        dbname=os.environ['PG_DATABASE'],
        user=os.environ['PG_USER'],
        password=os.environ['PG_PASSWORD'],
        # TCP keepalive prevents silent drops after firewall idle timeout
        keepalives=1,
        keepalives_idle=60,
        keepalives_interval=10,
        keepalives_count=5,
    )
    register_vector(conn)       # MUST be per-connection — not at module level
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_db_settings() -> dict[str, str]:
    return {
        'host': os.environ.get('PG_HOST', '10.0.0.87'),
        'port': os.environ.get('PG_PORT', '5432'),
        'database': os.environ.get('PG_DATABASE', 'opportunity_bot'),
        'storage': 'pgvector (Xeon)',
    }
```

**Why context manager, not raw return:** psycopg2 connections hold open transactions. Without explicit `close()`, crashed processes leave `idle in transaction` connections that hold row locks until PostgreSQL's idle timeout fires (disabled by default). The `@contextmanager` guarantees cleanup on any exit path including `KeyboardInterrupt`.

**Why no `query_by_similarity()` in config_db.py:** Three callers need different WHERE clauses (advisor: `investment_min <= 200 AND score >= 60`, personalization engine: credit-score-based filter, query CLI: no filter). A shared function would require 5+ optional parameters and becomes harder to understand than three short inline SQL strings. Each caller writes its own SQL directly.

**1.2 Update `production_opportunity_pipeline.py`**

Major changes:
- Replace ChromaDB import with `from config_db import get_pgvector_connection`
- Replace `SentenceTransformer` import with `from embeddings import encode`
- Replace `hash(url) % 10000` with `uuid5(NAMESPACE_URL, url)` for doc_id
- Add LLM result cache (see 1.8)
- Batch all embeddings after scraping, before INSERT
- Use `execute_values` with ON CONFLICT UPDATE for re-analysis support
- Open connection with `with get_pgvector_connection() as conn:` wrapping the entire pipeline run
- Apply `validate_analysis()`, `coerce_to_list()`, `parse_investment_range()`, `normalize_priority()` before INSERT

**ON CONFLICT UPDATE pattern (supports re-analysis on version bump):**
```sql
INSERT INTO business_opportunities
    (doc_id, title, url, source, ..., analysis_version, analyzed_at)
VALUES %s
ON CONFLICT (url) DO UPDATE SET
    automation_score   = EXCLUDED.automation_score,
    legitimacy_score   = EXCLUDED.legitimacy_score,
    recommended_action = EXCLUDED.recommended_action,
    key_insights       = EXCLUDED.key_insights,
    risks              = EXCLUDED.risks,
    analysis_version   = EXCLUDED.analysis_version,
    analyzed_at        = EXCLUDED.analyzed_at
WHERE business_opportunities.analysis_version < EXCLUDED.analysis_version;
-- The WHERE clause ensures same-version re-runs are idempotent (no-op)
```

**For pre-normalized vectors, use `<#>` at query time:**
```sql
-- Similarity search (pre-normalized vectors → use inner product <#>)
SELECT title, source, url, automation_score, 1 + (embedding <#> %s) AS similarity
FROM business_opportunities
WHERE embedding IS NOT NULL
ORDER BY embedding <#> %s
LIMIT %s
```

**For filtered queries (advisor), enable iterative scan:**
```sql
-- In advisor queries — enables pgvector 0.8.0+ iterative HNSW scan
SET LOCAL hnsw.ef_search = 100;
SET LOCAL hnsw.iterative_scan = 'relaxed_order';

SELECT title, url, automation_score, initial_investment_min_usd
FROM business_opportunities
WHERE initial_investment_min_usd <= 200
  AND automation_score >= 60
  AND embedding IS NOT NULL
ORDER BY embedding <#> %s
LIMIT 5;
```

**1.3 Add `embeddings.py`** (see module spec above)

**1.4 Update `query_opportunities.py`**
- Use `with get_pgvector_connection() as conn:`
- Use `from embeddings import encode` for query vector
- Fix KeyError: remove reads of `time_to_market`, `tech_stack` (not stored in old schema); read from new pgvector columns

**1.5 Fix `credit_integration/personalization_engine.py`**
- Line 88: replace `chromadb.PersistentClient` with `get_pgvector_connection()` context manager
- Remove `rag_db_path: Path` parameter from `__init__` signature
- Open connection within each `_query_rag()` call using `with get_pgvector_connection() as conn:` (keep stateless — avoids long-lived connection in `__init__`)
- Fix falsy-int: `if self.credit_score` → `if self.credit_score is not None`

**1.6 Fix `list_automation_opportunities.py`**
Four separate bugs to fix:
```python
# OLD (wrong — four bugs)
collection = client.get_collection("opportunities")   # wrong name
revenue_potential = metadata.get('revenue_potential') # wrong field
investment_required = metadata.get('investment_required') # not stored
source_url = metadata.get('source_url')              # wrong field

# NEW (correct)
# via pgvector SQL:
# SELECT revenue_claim, url FROM business_opportunities ...
```

**1.7 Update `scrapers/__init__.py`**
```python
# Add the two missing scrapers:
from scrapers.hackernews_scraper import HackerNewsScraper
from scrapers.producthunt_scraper import ProductHuntScraper

__all__ = ['RedditScraper', 'IndieHackersScraper', 'GoogleDorkingScraper',
           'HackerNewsScraper', 'ProductHuntScraper']
```
(RedditPublicScraper will also be added when created in W2)

**1.8 Add LLM result cache (highest performance impact)**

SQLite cache keyed by URL hash. Before calling `analyze_with_qwen()`, check cache. At 90% cache hit rate: 150 opportunities → 15 uncached inferences → ~11 minutes vs 112 minutes.

```python
# llm_cache.py — simple SQLite cache
import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

CACHE_PATH = Path('data/llm_cache.sqlite')

def _get_cache_conn():
    conn = sqlite3.connect(CACHE_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS llm_cache (
            url_hash TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            analysis_json TEXT NOT NULL,
            model_version TEXT NOT NULL DEFAULT '1',
            cached_at TEXT NOT NULL
        )
    """)
    return conn

def get_cached_analysis(url: str, model_version: str = '1') -> dict | None:
    url_hash = str(uuid.uuid5(uuid.NAMESPACE_URL, url))
    with _get_cache_conn() as conn:
        row = conn.execute(
            "SELECT analysis_json FROM llm_cache WHERE url_hash = ? AND model_version = ?",
            (url_hash, model_version)
        ).fetchone()
    return json.loads(row[0]) if row else None

def cache_analysis(url: str, analysis: dict, model_version: str = '1'):
    url_hash = str(uuid.uuid5(uuid.NAMESPACE_URL, url))
    with _get_cache_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO llm_cache VALUES (?, ?, ?, ?, ?)",
            (url_hash, url, json.dumps(analysis), model_version,
             datetime.now(timezone.utc).isoformat())
        )
```

In `analyze_with_qwen()`:
```python
cached = get_cached_analysis(opportunity['url'])
if cached:
    return cached
analysis = call_qwen(opportunity)  # slow path
cache_analysis(opportunity['url'], analysis)
return analysis
```

**1.9 Fix `hackernews_scraper.py` and `producthunt_scraper.py`**
- Rename `scraped_date` → `created` in both files (matches established `reddit_scraper.py` pattern)
- Remove duplicate `revenue_potential` key (keep only `revenue_claim`)
- Fix ProductHunt O(n²) URL dedup: replace `if url not in [p.get('url') for p in products]` with `seen_urls = set()` maintained outside the loop
- Fix unreachable code block in `hackernews_scraper.py` lines 118-170 (dead code after `return`)

**1.10 Update `requirements.txt`**
```
psycopg2-binary>=2.9
pgvector>=0.8.0        # 0.8.0+ required for hnsw.iterative_scan
sentence-transformers>=3.0
```

---

#### Phase 2: No-Auth Reddit Scraper (W2)

**2.1 Create `scrapers/reddit_public_scraper.py`**

```python
from typing import TypedDict

class ScrapedRecord(TypedDict):
    title: str
    description: str
    source: str
    url: str
    score: int
    created: str       # ISO datetime — matches established pattern
    revenue_claim: str
    tech_stack: str
    # time_mentioned REMOVED — always "Not specified", not in pgvector schema
```

Public JSON API endpoint:
```
GET https://www.reddit.com/r/{subreddit}/search.json
    ?q={query}&restrict_sr=true&sort=new&t=month&limit=100
Headers: User-Agent: python:com.isnbiz.opportunitybot:v2.0 (by /u/YOUR_REDDIT_USERNAME)
```

**Rate limiting (corrected for this scraper's context):**
- Unauthenticated (no OAuth): 10 req/min → `time.sleep(6)` between requests
- If PRAW OAuth credentials are configured: 60 req/min → `time.sleep(1)` is sufficient
- The public JSON scraper (no credentials) must use 6-second delay

**Do NOT re-implement `extract_revenue()` or `extract_tech_stack()`:**
- Check which existing scraper has the most complete version (`reddit_scraper.py` lines 40, 63)
- Import from that module: `from scrapers.reddit_scraper import extract_revenue, extract_tech_stack` (as standalone functions)
- If they are instance methods, extract to module-level functions in `scrapers/utils.py`

Use `requests.Session` (reuse TCP connections, ~50ms savings per request):
```python
import requests
import time

class RedditPublicScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'python:com.isnbiz.opportunitybot:v2.0 (by /u/YOUR_REDDIT_USERNAME)'
        })

    def _get(self, url: str) -> dict | None:
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 429:
                time.sleep(60)          # back off 60s on rate limit
                resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get('error'):       # Reddit returns error in JSON body too
                return None
            return data
        except Exception:
            return None
        finally:
            time.sleep(6)               # 10 req/min unauthenticated
```

**2.2 Wire into `production_opportunity_pipeline.py`**

Add `RedditPublicScraper` as a fourth source. Add `--source reddit` to argument parser. Remove the orphaned `from scrapers.reddit_scraper import RedditScraper` import.

**2.3 Update `scrapers/config.py`**
- Remove `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` env var reads
- Keep `REDDIT_SUBREDDITS` and `REDDIT_SEARCH_QUERIES`
- Add proper Reddit User-Agent env var: `REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'python:com.isnbiz.opportunitybot:v2.0 (by /u/unknown)')`

---

#### Phase 3: Credit Data Ingestion + Advisor (W3)

**3.1 Add `personal_fico_score` to `CreditProfile`**

```python
# In credit_integration/fico_parser.py
@dataclass
class CreditProfile:
    # ... existing fields ...
    personal_fico_score: int | None = None  # int | None (Python 3.10+ style for new code)

    def __post_init__(self) -> None:
        """Validate ranges on construction."""
        if self.personal_fico_score is not None:
            if not (300 <= self.personal_fico_score <= 850):
                raise ValueError(
                    f"personal_fico_score {self.personal_fico_score} outside FICO range 300-850"
                )
```

No `personal_fico_available: bool` — redundant with `personal_fico_score is not None`.

**3.2 Rewrite `calculate_risk_profile()` in `fico_parser.py`**

Fix falsy-int bug AND add personal FICO override:

```python
def calculate_risk_profile(self) -> RiskProfile:
    # Fix: is not None (not truthy check — score of 0 would fail truthy check)
    has_business_score = self.credit_score is not None
    has_personal_fico = self.personal_fico_score is not None

    if has_business_score and self.credit_score < 500 and not has_personal_fico:
        return RiskProfile.CONSERVATIVE

    if has_business_score and self.credit_score < 500 and has_personal_fico and self.personal_fico_score >= 720:
        return RiskProfile.MODERATE   # personal credit is the actual funding lever

    if (not has_business_score or self.credit_score >= 700) and \
       self.payment_index >= 90 and \
       has_personal_fico and self.personal_fico_score >= 750:
        return RiskProfile.AGGRESSIVE

    return RiskProfile.MODERATE
```

**3.3 Rewrite `calculate_max_investment()`** — (same as Round 1 spec, unchanged)

**3.4 Remove hardcoded profiles from `fico_parser.py` — WITH REPLACEMENT**

`create_isnbiz_profile()` and `create_hroc_profile()` are actively used in `personalized_opportunity_bot.py` production logic (not just demos). Removal requires updating `personalized_opportunity_bot.py`:

```python
# personalized_opportunity_bot.py — replacement bootstrapping
def _load_or_create_profile(business_entity: str, profile_file: Path) -> CreditProfile:
    if profile_file.exists():
        return FICOParser.load_profile(profile_file)
    # First-time: load from assessment doc (replaces hardcoded factory methods)
    from credit_integration.credit_data_ingestion import load_from_assessment_doc
    assessment_path = Path('CREDIT_ASSESSMENT_2026-02-04.md')
    if assessment_path.exists():
        profile = load_from_assessment_doc(assessment_path)
    else:
        raise FileNotFoundError(
            f"No profile file at {profile_file} and no assessment doc at {assessment_path}. "
            "Run credit setup first."
        )
    # Save to profile file for next time (outside repo — see security notes)
    profile_file.parent.mkdir(parents=True, exist_ok=True)
    FICOParser.save_profile(profile, profile_file)
    return profile
```

Profile file path should be `~/.opportunity-bot/profiles/{entity}.json` (outside git repo).

**3.5 Create `credit_integration/credit_data_ingestion.py`**

```python
# Module-level function (no class)
def load_from_assessment_doc(path: Path) -> CreditProfile:
    """
    Parse CREDIT_ASSESSMENT_*.md and return a populated CreditProfile.

    Raises FileNotFoundError if path does not exist.
    Raises ValueError if FICO scores cannot be parsed (with exact count found).
    """
    if not path.exists():
        raise FileNotFoundError(f"Credit assessment doc not found: {path}")

    text = path.read_text(encoding='utf-8')   # explicit encoding — Windows defaults to cp1252

    # Parse personal FICO scores from Markdown table with bold markers
    # Matches: | Equifax | **788** | Very Good |
    patterns = {
        'equifax':    r'\|\s*Equifax\s*\|\s*\**(\d{3})\**\s*\|',
        'transunion': r'\|\s*Trans[Uu]nion\s*\|\s*\**(\d{3})\**\s*\|',
        'experian':   r'\|\s*Experian\s*\|\s*\**(\d{3})\**\s*\|',
    }
    scores = {}
    for bureau, pattern in patterns.items():
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            score = int(m.group(1))
            if not (300 <= score <= 850):
                raise ValueError(f"{bureau} score {score} outside valid FICO range 300-850")
            scores[bureau] = score

    if len(scores) < 3:
        raise ValueError(
            f"Expected 3 bureau FICO scores, found {len(scores)}: {list(scores.keys())}. "
            "Check regex patterns against document format."
        )

    personal_fico = min(scores.values())   # conservative: use lowest bureau

    # Return ISNBIZ profile with personal FICO injected
    return CreditProfile(
        business_name="ISNBIZ, INCORPORATED",
        credit_score=372,
        payment_index=80,
        available_credit=137,
        credit_limit=137,
        derogatory_marks=0,
        sbss_score=210,
        years_in_business=2.0,
        personal_fico_score=personal_fico,
    )
```

No `load_from_json()` / `save_to_json()` — delegate to `FICOParser.load_profile()` / `FICOParser.save_profile()`.

**3.6 Create `credit_integration/advisor.py`**

Follows `@dataclass` pattern (matching `credit_scorer.py` — not plain dict, which was Round 1's incorrect recommendation):

```python
from dataclasses import dataclass, field, asdict

@dataclass
class OpportunityMatch:
    doc_id: str          # for CRUD back-reference from agent tools
    title: str
    url: str
    automation_score: int
    investment_min_usd: float
    investment_max_usd: float
    why_now: str = ''    # advisor-generated reasoning for this credit tier
    next_action: str = ''

@dataclass
class AdvisoryReport:
    generated_at: str
    expires_at: str          # 24h expiry — tells consuming agent when to refresh
    credit_tier: str
    personal_fico: int | None
    sbss: int | None
    immediate: list[OpportunityMatch] = field(default_factory=list)   # <= $200
    short_term: list[OpportunityMatch] = field(default_factory=list)   # $200-$5K
    fund_and_grow_eligible: bool = False
    sba_eligible: bool = False
    credit_building_steps: list[dict] = field(default_factory=list)    # structured dicts
    summary: str = ''
```

Module-level functions:
```python
def get_immediate_opportunities(conn, credit_profile: CreditProfile, n: int = 5) -> list[OpportunityMatch]:
    """Opportunities under $200 with automation_score >= 60."""
    ...

def get_tiered_advice(conn, credit_profile: CreditProfile) -> AdvisoryReport:
    """Build full tiered report."""
    ...

def run_advisor(credit_profile: CreditProfile) -> None:
    """Main entry point: query, print, write JSON output."""
    with get_pgvector_connection() as conn:
        report = get_tiered_advice(conn, credit_profile)

    # Print to stdout
    _print_report(report)

    # Write structured JSON for agent tooling
    output_dir = Path('reports/advisor')
    output_dir.mkdir(parents=True, exist_ok=True)   # create if missing

    report_dict = asdict(report)
    # Atomic write (prevents partial files on crash/disk-full)
    import tempfile
    for path in [output_dir / 'latest.json']:        # ONLY latest.json (no dated archive for week-1)
        with tempfile.NamedTemporaryFile(mode='w', dir=output_dir,
                                        suffix='.tmp', delete=False, encoding='utf-8') as tmp:
            json.dump(report_dict, tmp, indent=2, default=str)
            tmp_path = Path(tmp.name)
        tmp_path.replace(path)   # atomic on POSIX and Windows same-volume
```

**SBSS threshold for SBA eligibility:**
```python
SBA_ELIGIBLE_THRESHOLD = 155    # last SBA official floor (165 was raised June 2025, sunset March 2026)
                                 # lender practical floor is 175-180; 155 is the eligibility gate
                                 # SBSS 210 clears all thresholds comfortably
fund_and_grow_threshold = 720    # operational threshold (680 is paper floor, 720 for meaningful limits)
```

**Advisor JSON output fields for agent consumption** (additions to plain dict/dataclass):
- `generated_at` and `expires_at` (24h) — agent knows when to refresh
- `doc_id` on each `OpportunityMatch` — enables CRUD back-reference
- `why_now` and `next_action` on each match — agent-generated context

**3.7 Update `PersonalizationEngine`**

Fix falsy-int and add FICO query enhancement (per Round 1 spec, unchanged).

---

## Agent-Native Patterns

### Current Gap vs. Agent-Native Target

The pipeline is a one-shot script ("request/response thinking"). An agent-native version exposes primitives:

```python
# Add these standalone callable functions alongside the existing pipeline:
def scrape_source(source_name: str) -> list[dict]: ...          # agent can call per-source
def analyze_opportunity(raw: dict) -> dict: ...                  # agent can call per-opp
def store_opportunity(analyzed: dict) -> str: ...               # returns doc_id
def search_opportunities(query: str, filters: dict = None, limit: int = 10) -> list[dict]: ...
def get_opportunity(doc_id: str) -> dict: ...
def update_opportunity(doc_id: str, updates: dict) -> str: ...  # for advisor to mark "pursued"
```

### Pipeline Context File

Create `data/pipeline_context.md` (updated at end of every run) so an agent reading it at session start has full situational awareness:

```markdown
# Pipeline Context

## Last Run: 2026-02-26T08:00:00Z
- Sources: Reddit (42), HN (31), PH (28), IH (19)
- New stored: 101 | Cache hits: 89 | Skipped (duplicate): 67

## Database State
- Total opportunities: 1,847 | pgvector (Xeon 10.0.0.87:5432)

## Credit Profile (last refreshed: 2026-02-04)
- Personal FICO: 763 (min bureau) | SBSS: 210/300 | Tier: MODERATE

## Known Issues
- Reddit public JSON: 6s delay between requests (unauthenticated)
```

### Completion Signal

```python
def complete_pipeline_run(stats: dict) -> None:
    """Write structured completion artifact for cron/orchestrator handshake."""
    reports_dir = Path('reports/runs')
    reports_dir.mkdir(parents=True, exist_ok=True)
    output = {'completed_at': datetime.now(timezone.utc).isoformat(), **stats}
    (reports_dir / 'latest.json').write_text(json.dumps(output, indent=2))
```

---

## Xeon Always-On Architecture

### Transition: Cron → systemd Daemon

**Step 1 (now):** Keep one-shot script; add LLM cache and batch embeddings.

**Step 2 (after W1+W2+W3 working):** Convert to systemd daemon with asyncio producer/consumer:

```ini
# /etc/systemd/system/opportunity-bot.service
[Unit]
Description=Opportunity Bot - Continuous Scraping Pipeline
After=network-online.target postgresql.service redis.service
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/opportunity-research-bot
EnvironmentFile=/opt/opportunity-research-bot/.env
ExecStart=/opt/opportunity-research-bot/venv/bin/python production_opportunity_pipeline.py
Restart=on-failure
RestartSec=30s
StartLimitBurst=3
StartLimitIntervalSec=300
TimeoutStopSec=120s    # gives current document time to finish before SIGKILL
StandardOutput=journal
StandardError=journal
SyslogIdentifier=opportunity-bot

[Install]
WantedBy=multi-user.target
```

**Graceful shutdown** (handles SIGTERM from systemd stop):
```python
import signal, threading
shutdown_event = threading.Event()

def _handle_shutdown(signum, frame):
    shutdown_event.set()   # fast, non-blocking

signal.signal(signal.SIGTERM, _handle_shutdown)
signal.signal(signal.SIGINT, _handle_shutdown)

# In main loop:
for opp in opportunities:
    if shutdown_event.is_set():
        break          # finish current document (already analyzed), then exit
    analysis = analyze_with_qwen(opp)
    store(opp, analysis)
```

**Redis seen-URL dedup cache (replaces in-process set):**
```python
import redis
r = redis.Redis(host='10.0.0.87', port=6379, decode_responses=True)

def is_seen(url: str) -> bool:
    return r.zscore('opportunity_bot:seen_urls', url_hash(url)) is not None

def mark_seen(url: str, ttl_days: int = 30):
    import time
    r.zadd('opportunity_bot:seen_urls', {url_hash(url): time.time() + ttl_days * 86400})
```

**Xeon parallel LLM workers (4x throughput):**
- Run 4 llama-server instances on ports 8080-8083, each pinned to 18 cores via `numactl`
- Use `ProcessPoolExecutor(max_workers=4)` distributing `analyze_with_qwen` across ports
- With LLM cache (90% hit rate) + 4 workers: 150 opps → 15 uncached × 45s / 4 workers = ~3 min analysis

---

## Alternative Approaches Considered

| Approach | Rejected Because |
|----------|-----------------|
| RAG API at :8400 (FastAPI wrapper around ChromaDB) | Adds a service layer with no benefit when all consumers are Python; pgvector gives richer SQL |
| Keep ChromaDB + migrate gradually | YAGNI; two databases add operational overhead; 39% existing data is duplicate demo entries |
| PRAW with read-only OAuth | Still requires credentials; public JSON API is credential-free |
| snscrape for Reddit | Reddit support deprecated |
| `query_by_similarity()` in config_db.py | Three callers need different queries; shared function requires 5+ optional params; inline SQL is clearer |
| Plain dict for advisor output | `credit_scorer.py` uses `@dataclass` (`MatchScore`); domain pattern uses dataclasses; plain dicts lose type safety |
| `YYYY-MM-DD.json` dated archive | No consumer exists for week-1; add when a reader exists |
| `time_mentioned` in ScrapedRecord | Always "Not specified"; not in pgvector schema; dead weight |
| `analysis_version TEXT` | Lexicographic ordering fails (`'1.9' > '1.10'`); INTEGER is unambiguous |

---

## System-Wide Impact

### Interaction Graph

```
production_opportunity_pipeline.py
    └── run_full_pipeline()
            ├── with get_pgvector_connection() as conn:  [single context manager per run]
            ├── from embeddings import encode(all_docs)  [singleton model, batch encode]
            ├── get_cached_analysis(url) → skip if hit   [llm_cache.py SQLite]
            └── execute_values(INSERT ... ON CONFLICT DO UPDATE WHERE analysis_version < ...)

query_opportunities.py
    └── with get_pgvector_connection() as conn:
            └── SELECT ... ORDER BY embedding <#> %s     [inner product, pre-normalized]

personalization_engine.py
    └── _query_rag()
            └── with get_pgvector_connection() as conn:  [per-call, not per-__init__]
                    └── credit_scorer.batch_score_opportunities() [returns MatchScore dataclass]

advisor.py
    └── run_advisor(credit_profile: CreditProfile)
            └── with get_pgvector_connection() as conn:
                    ├── SET LOCAL hnsw.iterative_scan = 'relaxed_order'
                    ├── SET LOCAL hnsw.ef_search = 100
                    ├── SELECT WHERE initial_investment_min_usd <= 200 AND automation_score >= 60
                    └── write reports/advisor/latest.json (atomic rename)
```

### Error Propagation

- Xeon Postgres unreachable: `psycopg2.OperationalError` propagates from `get_pgvector_connection()` context manager
- Assessment doc not found: `FileNotFoundError` from `load_from_assessment_doc()` (descriptive message with path)
- Assessment doc with bad FICO regex: `ValueError` with count of found vs expected 3 bureau scores
- File open without `encoding='utf-8'`: `UnicodeDecodeError` on Windows — encoding is explicit in all file operations
- Reddit 429: 60s sleep + one retry; on second failure, log and skip that subreddit (no pipeline abort)
- LLM cache write fails (disk full): log warning, skip cache write, continue with uncached analysis

### State Lifecycle Risks

- **Duplicate documents**: `url NOT NULL UNIQUE` + `ON CONFLICT DO UPDATE` → re-analysis updates, not silently drops
- **Partial pipeline run**: context manager rollback on crash; already-committed rows are safe
- **Partial file write**: atomic rename for `latest.json` prevents partial JSON reads
- **Stale embeddings**: `embedding_status` column distinguishes retry-able failures from permanent skips
- **Profile files in repo**: `~/.opportunity-bot/profiles/` path keeps them outside git tree

### Integration Test Scenarios

1. **Full pipeline → query**: Demo mode → store one opp → query returns it via `<#>` similarity
2. **Credit override**: `CreditProfile(credit_score=372, personal_fico_score=763)` → `calculate_risk_profile()` returns MODERATE
3. **Advisor zero results**: `run_advisor()` against empty table → prints actionable message, not exception
4. **Reddit scraper**: `scrape_all()` returns ≥1 result without credentials
5. **Duplicate detection**: Insert same URL twice → one row in table (ON CONFLICT semantics)
6. **LLM cache hit**: analyze URL → cache result → analyze again → returns cached, no Qwen call
7. **`scalability_score` range validation**: LLM returns `"scalability": 4` (1-5 scale) → stored as 4 → passes `CHECK (BETWEEN 1 AND 5)`

---

## Acceptance Criteria

### Pre-Work (Security — must complete before W1)

- [ ] `git show 4558a05:credit_integration/profiles/test_isnbiz.json` checked; file purged from git history
- [ ] `credit_integration/profiles/` added to `.gitignore`
- [ ] `reports/` and `reports/advisor/` added to `.gitignore`
- [ ] `CREDIT_ASSESSMENT_*.md` added to `.gitignore`
- [ ] `--no-verify` instruction removed from `CLAUDE.md`
- [ ] Profile output path changed to `~/.opportunity-bot/profiles/` (outside repo)

### Workstream 1: pgvector

- [ ] `config_db.py` provides `get_pgvector_connection()` as `@contextmanager`
- [ ] `register_vector()` called inside `get_pgvector_connection()` per connection (NOT at module level)
- [ ] `get_pgvector_connection()` commits on success, rolls back on exception, always closes
- [ ] `create_schema()` is in `scripts/setup_pgvector.py` (NOT inside `config_db.py`)
- [ ] Schema has `scalability_score CHECK (BETWEEN 1 AND 5)` (matches LLM prompt 1-5 scale)
- [ ] Schema has `recommended_action CHECK (IN ('high','medium','low'))` (not dropped)
- [ ] Schema has `initial_investment_min_usd` AND `initial_investment_max_usd` (two columns)
- [ ] Schema has `embedding_status TEXT NOT NULL DEFAULT 'pending'`
- [ ] Schema has `analysis_version INTEGER NOT NULL DEFAULT 1` (not TEXT)
- [ ] Schema has `key_insights TEXT[] NOT NULL DEFAULT '{}'` and `risks TEXT[] NOT NULL DEFAULT '{}'`
- [ ] HNSW index uses `vector_ip_ops` (inner product for pre-normalized vectors)
- [ ] `embeddings.py` module provides lazy singleton `get_model()` and `encode(texts)` function
- [ ] `production_opportunity_pipeline.py` uses `uuid5(NAMESPACE_URL, url)` for doc_id
- [ ] `production_opportunity_pipeline.py` uses `execute_values` with ON CONFLICT UPDATE WHERE version check
- [ ] `production_opportunity_pipeline.py` calls `coerce_to_list()` for TEXT[] columns before INSERT
- [ ] `production_opportunity_pipeline.py` calls `parse_investment_range()` for both min/max columns
- [ ] `production_opportunity_pipeline.py` calls `normalize_priority()` for `recommended_action`
- [ ] LLM result cache (`llm_cache.py`) checks by url hash before calling Qwen; caches result after
- [ ] Queries use `<#>` operator (inner product) not `<=>` (cosine) for pre-normalized vectors
- [ ] Advisor queries use `SET LOCAL hnsw.iterative_scan = 'relaxed_order'` and `ef_search = 100`
- [ ] `query_opportunities.py` no longer reads `time_to_market` or `tech_stack` from metadata
- [ ] `personalization_engine.py` opens connection per `_query_rag()` call (not stored in `__init__`)
- [ ] `list_automation_opportunities.py` uses correct field names: `revenue_claim`, `url`
- [ ] `scrapers/__init__.py` exports `HackerNewsScraper` and `ProductHuntScraper`
- [ ] `hackernews_scraper.py` uses `created` (not `scraped_date`) key; no `revenue_potential` duplicate
- [ ] `producthunt_scraper.py` uses `created` key; no `revenue_potential` duplicate; O(n²) URL dedup fixed
- [ ] `hackernews_scraper.py` dead code block removed (lines 118-170)
- [ ] `data/pipeline_context.md` written at end of each pipeline run
- [ ] `complete_pipeline_run(stats)` writes `reports/runs/latest.json`
- [ ] `requirements.txt` includes `psycopg2-binary>=2.9`, `pgvector>=0.8.0`, `sentence-transformers>=3.0`
- [ ] Integration tests 1, 5, 6, 7 pass

### Workstream 2: Reddit scraper

- [ ] `scrapers/reddit_public_scraper.py` scrapes without credentials
- [ ] User-Agent includes `/u/yourusername` (Reddit ToS compliant)
- [ ] Returns `ScrapedRecord` TypedDict with 8 fields (no `time_mentioned`)
- [ ] Uses `time.sleep(6)` between requests (unauthenticated rate limit)
- [ ] Reddit 429 triggers 60s sleep + one retry before skipping
- [ ] Uses `requests.Session` (not per-request connection)
- [ ] Does NOT re-implement `extract_revenue()`/`extract_tech_stack()` — imports from existing module
- [ ] `RedditPublicScraper` added to `scrapers/__init__.py`
- [ ] Integration test 4 passes

### Workstream 3: Credit advisor

- [ ] `CreditProfile` has `personal_fico_score: int | None = None` with `__post_init__` range validation (300-850)
- [ ] All `if self.credit_score:` checks updated to `if self.credit_score is not None:`
- [ ] `calculate_risk_profile()` returns MODERATE when `personal_fico_score=763` and `credit_score=372`
- [ ] `credit_data_ingestion.py` opens assessment doc with `encoding='utf-8'`
- [ ] `load_from_assessment_doc()` raises `ValueError` with count if fewer than 3 bureau scores found
- [ ] `create_isnbiz_profile()` and `create_hroc_profile()` removed from `fico_parser.py`
- [ ] `personalized_opportunity_bot.py` uses `_load_or_create_profile()` replacement function
- [ ] `advisor.py` uses `AdvisoryReport` `@dataclass` with `OpportunityMatch` items
- [ ] Each `OpportunityMatch` includes `doc_id` for CRUD back-reference
- [ ] `AdvisoryReport` includes `generated_at` and `expires_at` (24h)
- [ ] `run_advisor()` writes `reports/advisor/latest.json` via atomic rename
- [ ] No dated `YYYY-MM-DD.json` archive (week-1 scope)
- [ ] `sba_eligible` flags when `sbss_score >= 155` (correct threshold)
- [ ] `fund_and_grow_eligible` flags when `personal_fico_score >= 720`
- [ ] Zero-results behavior: prints actionable message, not Python exception
- [ ] Integration tests 2, 3 pass

---

## Deployment Verification Checklist (Enhanced — 34 steps)

### Pre-Deploy

```bash
# 1. Check PostgreSQL version (must be >= 12 for pgvector 0.5+ HNSW support)
ssh user@10.0.0.87 "psql -U postgres -c 'SELECT version();'"
# Fail if: 10.x or 11.x — upgrade PostgreSQL before proceeding

# 2. Check pgvector extension available
ssh user@10.0.0.87 "psql -U postgres -c \"SELECT * FROM pg_available_extensions WHERE name = 'vector';\""
# If 0 rows: build pgvector from source (see install commands below)

# 3. Install pgvector from source if needed (Ubuntu/Debian)
ssh user@10.0.0.87 "
  PG_VER=\$(psql -U postgres -t -c 'SHOW server_version_num;' | xargs | cut -c1-2)
  sudo apt-get install -y postgresql-server-dev-\$PG_VER
  cd /tmp && git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
  cd pgvector && make && sudo make install
"

# 4. Tune PostgreSQL for HNSW index build
ssh user@10.0.0.87 "psql -U postgres -c \"SET maintenance_work_mem = '16GB'; SET max_parallel_maintenance_workers = 16;\""

# 5. Check Xeon internet access (for model download)
ssh user@10.0.0.87 "curl -s --max-time 5 https://huggingface.co > /dev/null && echo OK || echo NO_INTERNET"

# 6. Pre-download all-MiniLM-L6-v2 (on Xeon)
ssh user@10.0.0.87 "source /opt/opportunity-research-bot/venv/bin/activate &&
  python3 -c \"from sentence_transformers import SentenceTransformer;
  m = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2');
  e = m.encode(['test'], normalize_embeddings=True);
  assert len(e[0]) == 384, f'Wrong dimension: {len(e[0])}';
  print('Model OK, dim=384')\""

# 7. Create Linux venv on Xeon (NOT venv/Scripts/activate — that is Windows only)
ssh user@10.0.0.87 "cd /opt/opportunity-research-bot && python3.11 -m venv venv"
ssh user@10.0.0.87 "source /opt/opportunity-research-bot/venv/bin/activate && pip install psycopg2-binary 'pgvector>=0.8.0' 'sentence-transformers>=3.0'"

# 8. Baseline ChromaDB count before migration
python3 -c "
from config_chromadb import get_chroma_client
c = get_chroma_client()
col = c.get_collection('business_opportunities')
print(f'BASELINE: {col.count()} documents')
" 2>&1 | tee logs/pre_migration_baseline.txt
```

### Deploy Steps

```bash
# 9. Stop pipeline
pkill -f production_opportunity_pipeline.py

# 10. Run schema DDL (via setup script, NOT config_db.py)
ssh user@10.0.0.87 "source /opt/opportunity-research-bot/venv/bin/activate && python3 scripts/setup_pgvector.py"

# 11. Verify schema
ssh user@10.0.0.87 "psql -U postgres opportunity_bot -c \"\d business_opportunities\""
# Check: embedding column shows data_type = USER-DEFINED (pgvector), dim = 384

# 12. Build HNSW index WITH CONCURRENTLY (keeps table readable during build)
ssh user@10.0.0.87 "psql -U postgres opportunity_bot -c \"
  SET maintenance_work_mem = '16GB';
  CREATE INDEX CONCURRENTLY IF NOT EXISTS opp_embedding_hnsw
    ON business_opportunities
    USING hnsw (embedding vector_ip_ops)
    WITH (m = 32, ef_construction = 128)
    WHERE embedding IS NOT NULL;
\""

# 13. Verify HNSW index
ssh user@10.0.0.87 "psql -U postgres opportunity_bot -c \"SELECT indexname FROM pg_indexes WHERE tablename='business_opportunities' AND indexname LIKE '%hnsw%';\""

# 14. Deploy updated Python files
git pull  # or rsync from local

# 15. Demo run smoke test
python3 production_opportunity_pipeline.py --demo
```

### Post-Deploy Verification SQL

```sql
-- 16. Row count vs baseline
SELECT COUNT(*) FROM business_opportunities;

-- 17. No NULL embeddings (all rows should have embeddings after demo run)
SELECT COUNT(*) FROM business_opportunities WHERE embedding IS NULL;

-- 18. Embedding dimension is 384 for all rows
SELECT DISTINCT array_length(embedding::float4[], 1) FROM business_opportunities;

-- 19. Score ranges valid
SELECT COUNT(*) FILTER (WHERE automation_score < 0 OR automation_score > 100) AS bad_auto,
       COUNT(*) FILTER (WHERE scalability_score < 1 OR scalability_score > 5) AS bad_scale
FROM business_opportunities;

-- 20. HNSW index is being used (not Seq Scan)
EXPLAIN SELECT id FROM business_opportunities ORDER BY embedding <#> '[0.1,0.2,...]'::vector LIMIT 5;
-- Expected: "Index Scan using opp_embedding_hnsw"

-- 21. Investment range columns populated
SELECT COUNT(*) FILTER (WHERE initial_investment_min_usd IS NULL) AS missing_min
FROM business_opportunities;
```

### Rollback Procedure (Corrected)

```bash
# NOTE: config_chromadb.py was NEVER committed to git — git checkout will fail
# It was an untracked file. Rollback must use the working tree file directly.

# 22. Revert committed Python files (config_chromadb.py is NOT in this list)
git checkout HEAD -- production_opportunity_pipeline.py query_opportunities.py \
    credit_integration/personalization_engine.py credit_integration/fico_parser.py \
    list_automation_opportunities.py

# 23. Restore config_chromadb.py from backup (it was never committed)
# If you made a backup before starting: cp /backup/config_chromadb.py .
# If no backup: re-create from the Xeon ChromaDB http client pattern

# 24. Restart ChromaDB container (data is still on disk)
docker start <chroma_container_id>
python3 -c "import chromadb; c = chromadb.HttpClient(host='10.0.0.87', port=8000); c.heartbeat(); print('OK')"

# 25. Drop pgvector table
psql -h 10.0.0.87 -U postgres opportunity_bot -c "DROP TABLE IF EXISTS business_opportunities;"

# 26. Rollback verification
python3 query_opportunities.py "passive income"  # must return results
python3 -c "
from config_chromadb import get_chroma_client
c = get_chroma_client()
col = c.get_collection('business_opportunities')
print(f'Count after rollback: {col.count()}')
# Must match baseline from step 8
"
```

### Monitoring (First 24 Hours)

```sql
-- 27. Watch for active pipeline writes
SELECT state, left(query, 80) AS query, now()-query_start AS duration
FROM pg_stat_activity WHERE datname = 'opportunity_bot' AND state != 'idle';

-- 28. Table growth over time
SELECT COUNT(*), MAX(created_at) AS latest
FROM business_opportunities;

-- 29. HNSW index usage
SELECT idx_scan, pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes WHERE indexname = 'opp_embedding_hnsw';
```

```bash
# 30. systemd service status (after deploying as daemon)
sudo systemctl status opportunity-bot
journalctl -u opportunity-bot -f

# 31. Verify Linux crontab uses Linux venv path
crontab -l | grep activate
# Must show: venv/bin/activate (NOT venv/Scripts/activate)

# 32. LLM cache hit rate after first re-run
python3 -c "
import sqlite3
conn = sqlite3.connect('data/llm_cache.sqlite')
total = conn.execute('SELECT COUNT(*) FROM llm_cache').fetchone()[0]
print(f'Cached LLM results: {total}')
"

# 33. Redis seen-URL count (if Redis dedup is deployed)
redis-cli -h 10.0.0.87 ZCARD opportunity_bot:seen_urls

# 34. Advisor output exists and is parseable
python3 -c "import json; d = json.load(open('reports/advisor/latest.json')); print(d.get('credit_tier'), len(d.get('immediate', [])))"
```

---

## Dependencies & Prerequisites

| Dependency | Status | Blocks |
|------------|--------|--------|
| PostgreSQL >= 12 on Xeon | ❓ Verify version | W1 — pgvector 0.5+ (HNSW) requires PG 12+ |
| `pgvector >= 0.8.0` on Xeon | ❌ Not installed | W1 — 0.8.0 required for `hnsw.iterative_scan` |
| `CREDIT_ASSESSMENT_2026-02-04.md` | ✅ Present — ⚠️ Remove from git | W3 |
| `test_isnbiz.json` in git history | 🔴 Must purge (commit 4558a05) | Security pre-work |
| `credit_integration/profiles/` NOT in .gitignore | 🔴 Fix immediately | Security pre-work |
| Qwen3-30B-A3B @ 3.0bpw | 🔄 Downloading to Xeon | All (demo mode works without it) |
| `.env` with PG credentials | ❌ Not in `.env.tpl` yet | W1 |
| `reports/advisor/` directory | Created by `Path.mkdir(parents=True, exist_ok=True)` | W3 |
| `~/.opportunity-bot/profiles/` directory | Created by `_load_or_create_profile()` | W3 |
| `data/llm_cache.sqlite` | Created by `llm_cache.py` on first use | Performance (W1.8) |

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PostgreSQL version < 12 on Xeon (no HNSW support) | Medium | High | Check version first; Docker postgres:15 if needed |
| pgvector 0.8.0 not available as package (build from source) | Medium | Medium | 5-10 min build from source via `make && make install` |
| Xeon airgapped — all-MiniLM model can't download | Unknown | High | Pre-download on workstation; rsync to Xeon |
| `scalability_score` range mismatch with existing data | Certain for re-import | Low | Column is new; no existing pgvector data to migrate |
| `test_isnbiz.json` already pushed to GitHub | Check git log | High | git filter-repo purge + notify any collaborators |
| LLM cache corrupts analysis (stale cache after prompt change) | Low | Medium | `model_version` column in cache; bump version to invalidate |
| `create_isnbiz_profile()` removal breaks `personalized_opportunity_bot.py` | Certain (3 call sites) | High | `_load_or_create_profile()` replacement required before removal |
| Reddit 429 throttling kills scraping run | Medium | Medium | 60s backoff + retry; 6s between requests is conservative |
| Connection leak (context manager not used) | Medium (new code) | Medium | Code review criterion: every `get_pgvector_connection()` must be `with` block |

---

## Open Questions

1. **PostgreSQL version on Xeon**: Run `SELECT version()` — must be >= 12 for pgvector 0.5+ HNSW
2. **Xeon internet access**: `curl huggingface.co` — determines if model pre-download is needed
3. **Postgres credentials**: What `PG_USER`/`PG_PASSWORD` are configured on the Xeon?
4. **myFICO/Nav/D&B automation**: Credentials gate live credit data ingestion (markdown parse works without them)
5. **Qwen3-30B-A3B GPU or CPU**: Does Xeon have a GPU? CPU-only = 30-60s/opp; determines whether 4 llama-server instances are feasible

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Pipeline run without ChromaDB | ≥1 successful run storing to pgvector |
| LLM cache hit rate (second run) | ≥80% cache hits |
| Reddit opportunities stored | ≥10 after first run |
| Credit profile tier | MODERATE (not CONSERVATIVE) with FICO 763 |
| Advisor finds immediate opps | ≥1 with `initial_investment_min_usd <= 200` and `automation_score >= 60` |
| Week-1 income | $5+ from first deployed micro-service |

---

## Documentation Plan

- Update `.env.tpl`: add `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD`, `REDDIT_USER_AGENT`
- Update `CLAUDE.md`: replace `config_chromadb.py` → `config_db.py`; remove `--no-verify`; update activation command for Xeon (`venv/bin/activate`); add `reports/`, `credit_integration/profiles/`, `CREDIT_ASSESSMENT_*.md` to gitignore section
- Update `models.py`: `scalability_score: int = Field(ge=1, le=5)` (was ge=0, le=100)
- Mark `analyze_chromadb.py`, `inspect_sample_opportunities.py`, `generate_trends_report.py` as deprecated in `CLAUDE.md` with note: "These files query field names never stored in production (revenue_potential, investment_required, technical_difficulty). Update for pgvector or remove."

---

## Sources & References

### Origin
- **Brainstorm:** [`docs/brainstorms/2026-02-26-xeon-migration-credit-advisor-brainstorm.md`](../brainstorms/2026-02-26-xeon-migration-credit-advisor-brainstorm.md)
  - Key decisions: full pgvector migration, no-auth Reddit, personal FICO 763 as funding proxy

### Internal References
- `config_chromadb.py` — module-level function pattern; Xeon failover; **was never committed to git** (untracked for 25 days)
- `credit_integration/credit_scorer.py` — uses `@dataclass` (`MatchScore`) not plain dict; confirmed pattern for advisor
- `scrapers/__init__.py:6-10` — stale exports (missing HN, PH, future RedditPublicScraper)
- `scrapers/hackernews_scraper.py:71` — `scraped_date` key mismatch; lines 118-170 dead code
- `scrapers/producthunt_scraper.py` — O(n²) URL dedup; fake browser User-Agent
- `credit_integration/personalization_engine.py:88` — rogue `chromadb.PersistentClient` (broken TODAY)
- `list_automation_opportunities.py:10` — stale collection name AND wrong field names (revenue_potential, investment_required, source_url)
- `production_opportunity_pipeline.py:262` — `hash(url) % 10000` → `uuid5(NAMESPACE_URL, url)`
- `models.py:84` — `scalability_score: Field(ge=0, le=100)` must change to `ge=1, le=5`
- `personalized_opportunity_bot.py:71-75` — calls `create_isnbiz_profile()` / `create_hroc_profile()` (production logic)

### External References
- [pgvector 0.8.0 — iterative_scan parameter](https://github.com/pgvector/pgvector)
- [pgvector-python register_vector() per-connection pattern](https://github.com/pgvector/pgvector-python)
- Reddit public JSON API: `https://www.reddit.com/r/{sub}/search.json?q=...&restrict_sr=true`
- Reddit API ToS User-Agent format: `platform:app_id:version (by /u/username)`
- Reddit rate limits: 10 req/min unauthenticated; 60 req/min authenticated OAuth
- sentence-transformers `all-MiniLM-L6-v2`: 384 dims; `normalize_embeddings=True` for `<#>` operator
- HNSW `vector_ip_ops` (inner product) for pre-normalized vectors: mathematically equivalent to cosine, faster at query time
- `SET LOCAL hnsw.iterative_scan = 'relaxed_order'` for filtered HNSW queries (pgvector 0.8.0+)
- SBA SBSS threshold: 155 (last official), sunset March 1, 2026; lender practical floor 175-180
- Fund & Grow FICO threshold: 720 operational minimum (680 paper floor)
- psycopg2 `execute_values()` bulk insert: 40% faster than `execute_batch()`
- systemd `Restart=on-failure` + `TimeoutStopSec=120s` for graceful daemon shutdown
- asyncio + ProcessPoolExecutor producer/consumer for I/O-bound scraping + CPU-bound LLM

### Related Work
- `migrate_to_xeon.py` (untracked) — check for relevant migration patterns before writing `scripts/setup_pgvector.py`
- `scrapers/crawl4ai_base.py` — base class with `extract_revenue()` / `extract_tech_stack()` as module-level utilities (currently unused by production scrapers; consider extracting to `scrapers/utils.py`)

---

## Agent-Native Gap Analysis (Round 3 — agent-native-architecture skill)

**Deepened on:** 2026-02-26 (Round 3)
**Skill applied:** `agent-native-architecture` (SKILL.md + mcp-tool-design, agent-execution-patterns, action-parity-discipline, shared-workspace-architecture references)
**Context:** Xeon TabbyAPI at `http://100.65.249.20:8200/v1` (OpenAI-compatible Qwen3), `local-agent` MCP at `http://100.65.249.20:8300/sse` (ReAct), `rag-knowledge-base` MCP at `http://100.65.249.20:8301/sse`

Six gaps were identified in the prior code review. Each is addressed below with concrete specifications.

---

### Gap 1 — Agent-Native CRUD Stubs: File Location and Complete Signatures

**Problem:** The plan lists six stub functions in the "Agent-Native Patterns" section but gives no file location, no return types, and no error contracts. An implementer cannot write or test them.

**Skill principle applied:** CRUD Completeness + Primitives not Workflows. Every entity the agent can create it must also read, update, and delete. Tools accept data, not decisions. Outputs are rich enough for the agent to verify and iterate.

#### File: `opportunity_api.py` (project root, alongside `query_opportunities.py`)

This module is the **importable API layer**. It exposes atomic primitives over the pgvector store. The pipeline, advisor, query CLI, and `local-agent` MCP tools all import from here. Nothing in this file contains business logic — every function does exactly one database operation.

```python
# opportunity_api.py
"""
Atomic primitive API for the opportunity database.

All functions accept a live psycopg2 connection so callers control
transaction boundaries. No function opens its own connection — callers
use get_pgvector_connection() as the context manager.

Pattern:
    with get_pgvector_connection() as conn:
        result = get_opportunity(conn, doc_id)

Return convention:
    - get_*   → dict | None  (None means not found, never raises KeyError)
    - list_*  → list[dict]   (empty list on no results, never None)
    - store_* → str          (doc_id of stored/updated row)
    - update_* → bool        (True if row existed and was updated, False if not found)
    - delete_* → bool        (True if row existed and was deleted, False if not found)

All dict keys match column names in business_opportunities exactly.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import psycopg2.extensions
import psycopg2.extras

from embeddings import encode


# ---------------------------------------------------------------------------
# Type alias for callers
# ---------------------------------------------------------------------------
Conn = psycopg2.extensions.connection


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_opportunity(conn: Conn, doc_id: str) -> dict | None:
    """
    Return a single opportunity row as a dict, or None if not found.

    Args:
        conn:    Live psycopg2 connection (from get_pgvector_connection()).
        doc_id:  UUID5 identifier (e.g. str(uuid.uuid5(uuid.NAMESPACE_URL, url))).

    Returns:
        dict with all column values, or None if doc_id does not exist.
        The 'embedding' key is omitted from the returned dict (binary blob,
        not useful to callers; re-query with search_opportunities if needed).
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT id, doc_id, title, description, source, url, revenue_claim,
               automation_score, legitimacy_score, scalability_score,
               technical_difficulty, recommended_action,
               initial_investment, initial_investment_min_usd, initial_investment_max_usd,
               time_to_market, tech_stack, category, key_insights, risks,
               analysis_version, embedding_status, embedding_error,
               analyzed_at, created_at
        FROM business_opportunities
        WHERE doc_id = %s
        """,
        (doc_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def list_opportunities(
    conn: Conn,
    *,
    limit: int = 50,
    min_automation_score: int | None = None,
    max_investment_usd: float | None = None,
    source: str | None = None,
    embedding_status: str | None = None,
) -> list[dict]:
    """
    Return opportunities as a list of dicts, optionally filtered.

    All filter parameters are optional and combine with AND.
    Results are ordered by automation_score DESC, created_at DESC.
    The 'embedding' binary column is excluded from results.

    Args:
        conn:                  Live psycopg2 connection.
        limit:                 Max rows to return (default 50, max enforced by caller).
        min_automation_score:  Only rows with automation_score >= this value.
        max_investment_usd:    Only rows with initial_investment_min_usd <= this value.
        source:                Exact match on the 'source' column (e.g. 'reddit').
        embedding_status:      Exact match on embedding_status column
                               ('pending'|'processing'|'complete'|'failed'|'skipped').

    Returns:
        List of dicts (may be empty). Never None.
    """
    conditions: list[str] = []
    params: list[Any] = []

    if min_automation_score is not None:
        conditions.append("automation_score >= %s")
        params.append(min_automation_score)
    if max_investment_usd is not None:
        conditions.append("initial_investment_min_usd <= %s")
        params.append(max_investment_usd)
    if source is not None:
        conditions.append("source = %s")
        params.append(source)
    if embedding_status is not None:
        conditions.append("embedding_status = %s")
        params.append(embedding_status)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params.append(limit)

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        f"""
        SELECT id, doc_id, title, description, source, url, revenue_claim,
               automation_score, legitimacy_score, scalability_score,
               technical_difficulty, recommended_action,
               initial_investment, initial_investment_min_usd, initial_investment_max_usd,
               time_to_market, tech_stack, category, key_insights, risks,
               analysis_version, embedding_status, analyzed_at, created_at
        FROM business_opportunities
        {where_clause}
        ORDER BY automation_score DESC NULLS LAST, created_at DESC
        LIMIT %s
        """,
        params,
    )
    return [dict(row) for row in cur.fetchall()]


def search_opportunities(
    conn: Conn,
    query: str,
    *,
    limit: int = 10,
    min_automation_score: int | None = None,
    max_investment_usd: float | None = None,
) -> list[dict]:
    """
    Semantic similarity search using pgvector inner-product operator <#>.

    Encodes 'query' with all-MiniLM-L6-v2 (pre-normalized), then queries the
    HNSW index. For filtered queries, enables iterative scan so the index is
    used even when WHERE clauses exist.

    Args:
        conn:                  Live psycopg2 connection.
        query:                 Natural language query string.
        limit:                 Max results (default 10).
        min_automation_score:  Optional score floor.
        max_investment_usd:    Optional investment ceiling (initial_investment_min_usd).

    Returns:
        List of dicts with an additional 'similarity' float key (0.0-1.0).
        Ordered by similarity descending. Never None.
    """
    query_vec = encode([query])[0].tolist()

    conditions = ["embedding IS NOT NULL"]
    params: list[Any] = []

    if min_automation_score is not None:
        conditions.append("automation_score >= %s")
        params.append(min_automation_score)
    if max_investment_usd is not None:
        conditions.append("initial_investment_min_usd <= %s")
        params.append(max_investment_usd)

    where_clause = "WHERE " + " AND ".join(conditions)

    # Append the vector twice: once for SELECT expression, once for ORDER BY
    params_full = params + [query_vec, query_vec, limit]

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # Enable iterative HNSW scan for filtered queries (pgvector 0.8.0+)
    cur.execute("SET LOCAL hnsw.ef_search = 100")
    cur.execute("SET LOCAL hnsw.iterative_scan = 'relaxed_order'")
    cur.execute(
        f"""
        SELECT id, doc_id, title, description, source, url, revenue_claim,
               automation_score, legitimacy_score, recommended_action,
               initial_investment, initial_investment_min_usd, initial_investment_max_usd,
               key_insights, risks, analyzed_at, created_at,
               1 + (embedding <#> %s::vector) AS similarity
        FROM business_opportunities
        {where_clause}
        ORDER BY embedding <#> %s::vector
        LIMIT %s
        """,
        params_full,
    )
    return [dict(row) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# WRITE
# ---------------------------------------------------------------------------

def store_opportunity(conn: Conn, analyzed: dict) -> str:
    """
    Insert or update one opportunity. Idempotent via ON CONFLICT (url).

    The ON CONFLICT clause only applies the update when the incoming
    analysis_version is strictly greater than the stored version,
    so same-version re-runs are true no-ops.

    Args:
        conn:     Live psycopg2 connection. Caller commits via context manager.
        analyzed: Dict produced by analyze_opportunity(). Must contain at
                  minimum: title, url, source. All other keys are optional
                  and fall back to NULL or column defaults if absent.

    Returns:
        doc_id string (uuid5 of the url). Callers store this for later CRUD.

    Raises:
        psycopg2.IntegrityError: If NOT NULL constraint violated (missing
                                 required fields). Caller's context manager
                                 will rollback.
    """
    from config_db import _coerce_helpers  # parse_investment_range, normalize_priority, etc.

    url = analyzed["url"]
    doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, url))
    inv_min, inv_max = _coerce_helpers.parse_investment_range(
        analyzed.get("initial_investment", "") or ""
    )

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO business_opportunities (
            doc_id, title, description, source, url, revenue_claim,
            automation_score, legitimacy_score, scalability_score,
            technical_difficulty, recommended_action,
            initial_investment, initial_investment_min_usd, initial_investment_max_usd,
            time_to_market, tech_stack, category, key_insights, risks,
            analysis_version, embedding_status, analyzed_at
        ) VALUES (
            %(doc_id)s, %(title)s, %(description)s, %(source)s, %(url)s, %(revenue_claim)s,
            %(automation_score)s, %(legitimacy_score)s, %(scalability_score)s,
            %(technical_difficulty)s, %(recommended_action)s,
            %(initial_investment)s, %(inv_min)s, %(inv_max)s,
            %(time_to_market)s, %(tech_stack)s, %(category)s,
            %(key_insights)s, %(risks)s,
            %(analysis_version)s, 'pending', %(analyzed_at)s
        )
        ON CONFLICT (url) DO UPDATE SET
            automation_score        = EXCLUDED.automation_score,
            legitimacy_score        = EXCLUDED.legitimacy_score,
            scalability_score       = EXCLUDED.scalability_score,
            recommended_action      = EXCLUDED.recommended_action,
            key_insights            = EXCLUDED.key_insights,
            risks                   = EXCLUDED.risks,
            analysis_version        = EXCLUDED.analysis_version,
            embedding_status        = 'pending',
            analyzed_at             = EXCLUDED.analyzed_at
        WHERE business_opportunities.analysis_version < EXCLUDED.analysis_version
        RETURNING doc_id
        """,
        {
            "doc_id": doc_id,
            "title": analyzed.get("title", "")[:500],
            "description": analyzed.get("description", "")[:2000],
            "source": analyzed["source"],
            "url": url,
            "revenue_claim": analyzed.get("revenue_claim", "")[:200],
            "automation_score": analyzed.get("automation_score"),
            "legitimacy_score": analyzed.get("legitimacy_score"),
            "scalability_score": analyzed.get("scalability_score"),
            "technical_difficulty": analyzed.get("technical_difficulty"),
            "recommended_action": _coerce_helpers.normalize_priority(
                analyzed.get("recommended_action", "medium")
            ),
            "initial_investment": analyzed.get("initial_investment", ""),
            "inv_min": inv_min,
            "inv_max": inv_max,
            "time_to_market": analyzed.get("time_to_market"),
            "tech_stack": analyzed.get("tech_stack"),
            "category": analyzed.get("category"),
            "key_insights": _coerce_helpers.coerce_to_list(analyzed.get("key_insights")),
            "risks": _coerce_helpers.coerce_to_list(analyzed.get("risks")),
            "analysis_version": int(analyzed.get("analysis_version", 1)),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    # RETURNING returns the doc_id whether it was inserted or updated.
    # If the ON CONFLICT WHERE clause suppressed the update (same version),
    # fetchone() returns None — we still return the computed doc_id.
    row = cur.fetchone()
    return row[0] if row else doc_id


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def update_opportunity(conn: Conn, doc_id: str, updates: dict) -> bool:
    """
    Apply a partial update to one opportunity. Used by the advisor to mark
    opportunities as 'pursued', update embedding_status after backfill, or
    annotate with agent-generated notes.

    Only the keys present in 'updates' are modified. Unknown keys are
    silently ignored (do not raise — agent may pass extra context keys).

    Allowed update keys:
        embedding_status  ('pending'|'processing'|'complete'|'failed'|'skipped')
        embedding_error   (TEXT — error message if embedding_status='failed')
        recommended_action ('high'|'medium'|'low')
        category          (TEXT)
        analysis_version  (int — set when re-analyzing with new prompt version)
        analyzed_at       (ISO datetime string)

    Args:
        conn:     Live psycopg2 connection.
        doc_id:   UUID5 of the row to update.
        updates:  Dict of column name → new value. Only allowed keys applied.

    Returns:
        True if a row with that doc_id existed and was updated.
        False if doc_id not found (caller can log but should not raise).
    """
    ALLOWED = {
        "embedding_status", "embedding_error", "recommended_action",
        "category", "analysis_version", "analyzed_at",
    }
    filtered = {k: v for k, v in updates.items() if k in ALLOWED}
    if not filtered:
        # Nothing to update (all keys were unknown) — treat as no-op success
        return True  # don't return False: row may exist; we just had nothing to write

    set_clause = ", ".join(f"{k} = %({k})s" for k in filtered)
    filtered["doc_id"] = doc_id

    cur = conn.cursor()
    cur.execute(
        f"UPDATE business_opportunities SET {set_clause} WHERE doc_id = %(doc_id)s",
        filtered,
    )
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def delete_opportunity(conn: Conn, doc_id: str) -> bool:
    """
    Delete one opportunity by doc_id.

    Used when an opportunity is confirmed fraudulent, deprecated, or
    when a user explicitly asks the agent to remove it.

    Args:
        conn:    Live psycopg2 connection.
        doc_id:  UUID5 of the row to delete.

    Returns:
        True if a row was deleted. False if doc_id not found.
    """
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM business_opportunities WHERE doc_id = %s",
        (doc_id,),
    )
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# CONVENIENCE: scrape + analyze primitives (thin wrappers for agent callers)
# ---------------------------------------------------------------------------

def scrape_source(source_name: str) -> list[dict]:
    """
    Run a single scraper by name. Returns raw scraped records.

    Does not store anything — caller decides what to do with results.
    This is an atomic primitive: agent can call per-source and inspect
    results before storing.

    Args:
        source_name: One of 'reddit'|'indiehackers'|'hackernews'|'producthunt'.

    Returns:
        List of raw dicts (ScrapedRecord TypedDict shape). Empty list on
        error or rate-limit. Never raises — errors are logged and swallowed
        so the agent can try other sources.

    Raises:
        ValueError: If source_name is not a recognised scraper name.
    """
    from scrapers import (
        RedditPublicScraper,
        IndieHackersScraper,
        HackerNewsScraper,
        ProductHuntScraper,
    )
    scrapers = {
        "reddit": RedditPublicScraper,
        "indiehackers": IndieHackersScraper,
        "hackernews": HackerNewsScraper,
        "producthunt": ProductHuntScraper,
    }
    if source_name not in scrapers:
        raise ValueError(
            f"Unknown source '{source_name}'. Valid sources: {sorted(scrapers)}"
        )
    try:
        scraper = scrapers[source_name]()
        return scraper.scrape_all()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("scrape_source(%s) failed: %s", source_name, exc)
        return []


def analyze_opportunity(raw: dict) -> dict:
    """
    Run LLM analysis on one raw scraped record.

    Checks the SQLite LLM cache first. If cached, returns immediately
    without calling the LLM. Caches the result after a live call.

    Args:
        raw: A ScrapedRecord dict with at minimum 'url', 'title', 'description'.

    Returns:
        Dict with LLM-generated fields merged into the raw record:
        automation_score, legitimacy_score, scalability_score,
        technical_difficulty, recommended_action, initial_investment,
        time_to_market, tech_stack, key_insights, risks, analysis_version.

    Raises:
        RuntimeError: If the LLM call fails and no cache entry exists.
                      The error message includes the URL and raw LLM response
                      to aid debugging.
    """
    from llm_cache import get_cached_analysis, cache_analysis
    from production_opportunity_pipeline import analyze_with_qwen  # existing function

    cached = get_cached_analysis(raw["url"])
    if cached:
        return {**raw, **cached}

    analysis = analyze_with_qwen(raw)   # raises RuntimeError on failure
    cache_analysis(raw["url"], analysis)
    return {**raw, **analysis}
```

**CRUD audit for `business_opportunities` entity:**

| Operation | Function | Gap before |
|-----------|----------|------------|
| Create / upsert | `store_opportunity(conn, analyzed)` | Stub, no file or type |
| Read one | `get_opportunity(conn, doc_id)` | Missing entirely |
| Read many (filtered) | `list_opportunities(conn, ...)` | Missing entirely |
| Read many (semantic) | `search_opportunities(conn, query, ...)` | CLI-only, not importable |
| Update (partial) | `update_opportunity(conn, doc_id, updates)` | Stub, no file or type |
| Delete | `delete_opportunity(conn, doc_id)` | Missing entirely |

**Capability map — what `local-agent` MCP at :8300 can now achieve:**

| Agent request | Tool call | Notes |
|---|---|---|
| "Find opportunities under $200" | `search_opportunities(conn, q, max_investment_usd=200)` | semantic |
| "Show me opportunity abc-123" | `get_opportunity(conn, "abc-123")` | exact lookup |
| "Mark opportunity abc-123 as pursued" | `update_opportunity(conn, "abc-123", {"category": "pursued"})` | partial update |
| "Delete the fraudulent opportunity" | `delete_opportunity(conn, doc_id)` | requires doc_id from prior get |
| "Scrape Reddit and store new ones" | `scrape_source("reddit")` → loop `store_opportunity` | agent composes primitives |
| "List all pending embeddings" | `list_opportunities(conn, embedding_status="pending")` | filtered list |

---

### Gap 2 — Pipeline Running-State Artifact (`reports/runs/running.json`)

**Problem:** The plan has `complete_pipeline_run()` writing `reports/runs/latest.json` on success, but nothing distinguishes a running pipeline from a crashed one. An orchestrator or health-check script polling for output cannot tell the difference between "hasn't finished yet" and "died at step 3".

**Skill principle applied:** Completion Signals (agent-execution-patterns). The agent needs an explicit `complete_task` signal. Heuristic detection (checking if `latest.json` exists) is fragile. The solution here is two files: a `running.json` written at startup (tombstone), and a `latest.json` written at completion (signal).

#### Spec: `reports/runs/running.json`

Written atomically at the **start** of every pipeline run. Deleted (or replaced by `latest.json`) on clean exit. If the process crashes, `running.json` remains — that is the crash signal.

```json
{
  "started_at": "2026-02-26T08:00:00.000Z",
  "pid": 12345,
  "host": "xeon-gold-87",
  "sources": ["reddit", "hackernews", "producthunt", "indiehackers"],
  "stage": "scraping",
  "stage_started_at": "2026-02-26T08:00:01.123Z"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `started_at` | ISO 8601 UTC | When the run began. Orchestrator uses this to detect stale runs (>2h = assume crashed). |
| `pid` | int | OS process ID. Orchestrator can check `kill -0 <pid>` to distinguish crashed from still-running. |
| `host` | str | Hostname. Detects cross-host stale artifacts after migration. |
| `sources` | list[str] | Which scrapers were requested. Allows partial-run diagnosis. |
| `stage` | str | Current pipeline stage: `"init"` / `"scraping"` / `"analyzing"` / `"storing"` / `"embedding"`. |
| `stage_started_at` | ISO 8601 UTC | When current stage began. Detects stuck stages (e.g., LLM hung). |

**Stage update pattern (in `production_opportunity_pipeline.py`):**

```python
import json, os, socket
from pathlib import Path
from datetime import datetime, timezone
import tempfile

RUNS_DIR = Path("reports/runs")

def _write_running_state(stage: str, extra: dict | None = None) -> None:
    """Atomically update the running.json stage field."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_path = RUNS_DIR / "running.json"

    # Read existing state (preserves started_at, pid, host, sources)
    if run_path.exists():
        state = json.loads(run_path.read_text(encoding="utf-8"))
    else:
        state = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "sources": [],  # filled in by caller on init
        }

    state["stage"] = stage
    state["stage_started_at"] = datetime.now(timezone.utc).isoformat()
    if extra:
        state.update(extra)

    # Atomic write via temp file + rename
    with tempfile.NamedTemporaryFile(
        mode="w", dir=RUNS_DIR, suffix=".tmp", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(state, tmp, indent=2)
        tmp_path = Path(tmp.name)
    tmp_path.replace(run_path)


def complete_pipeline_run(stats: dict) -> None:
    """
    Write completion artifact and remove the running.json tombstone.
    Called ONLY on clean exit — crashed processes never reach this.
    """
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "success",
        **stats,
    }

    # Write latest.json atomically
    latest_path = RUNS_DIR / "latest.json"
    with tempfile.NamedTemporaryFile(
        mode="w", dir=RUNS_DIR, suffix=".tmp", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(output, tmp, indent=2)
        tmp_path = Path(tmp.name)
    tmp_path.replace(latest_path)

    # Remove the tombstone — its absence signals clean completion
    running_path = RUNS_DIR / "running.json"
    if running_path.exists():
        running_path.unlink()
```

**Orchestrator/health-check interpretation logic:**

```
running.json exists AND latest.json missing   → RUNNING (normal)
running.json absent  AND latest.json exists   → COMPLETED (normal)
running.json exists  AND latest.json exists   → RUNNING (last run completed, new run in progress)
running.json exists  AND started_at > 2h ago  → LIKELY CRASHED (check pid with kill -0)
running.json absent  AND latest.json absent   → NEVER RUN
```

---

### Gap 3 — Health-Check Endpoint / Script

**Problem:** No mechanism for the `local-agent` MCP at :8300 or an external orchestrator to poll whether the pipeline is healthy without SSHing into the Xeon.

**Skill principle applied:** Context Injection — the agent needs runtime state injected so it knows what exists and what is currently happening. A health-check script produces that state as machine-readable JSON.

#### Script: `scripts/health_check.py`

Designed to run in under 5 seconds. Writes JSON to stdout. Non-zero exit on any critical failure (see Gap 6 for exit codes).

```python
#!/usr/bin/env python3
"""
Health check for the opportunity bot.

Exit codes (see exit code table in plan):
    0  All systems healthy
    1  Partial degradation (pipeline not running, DB reachable)
    2  Critical failure (DB unreachable, or pipeline crashed)

Output: JSON to stdout.
Usage:
    python scripts/health_check.py
    python scripts/health_check.py --json   # same, explicit
    python scripts/health_check.py --quiet  # exit code only, no output
"""
from __future__ import annotations

import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

RUNS_DIR = Path("reports/runs")
ADVISOR_DIR = Path("reports/advisor")


def check_database() -> dict:
    """Attempt a cheap DB connection. Returns status dict."""
    try:
        from config_db import get_pgvector_connection
        with get_pgvector_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*), MAX(created_at) FROM business_opportunities"
            )
            count, latest = cur.fetchone()
        return {
            "status": "ok",
            "opportunity_count": count,
            "latest_opportunity_at": latest.isoformat() if latest else None,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def check_pipeline_state() -> dict:
    """Read running.json / latest.json and interpret state."""
    running_path = RUNS_DIR / "running.json"
    latest_path = RUNS_DIR / "latest.json"

    running = json.loads(running_path.read_text(encoding="utf-8")) if running_path.exists() else None
    latest = json.loads(latest_path.read_text(encoding="utf-8")) if latest_path.exists() else None

    if running and not latest:
        state = "running"
    elif not running and latest:
        state = "idle"
    elif running and latest:
        state = "running"  # new run started after last completion
    else:
        state = "never_run"

    # Crash detection: running.json older than 2 hours
    crashed = False
    if running:
        started = datetime.fromisoformat(running["started_at"])
        age_seconds = (datetime.now(timezone.utc) - started).total_seconds()
        if age_seconds > 7200:  # 2 hours
            # Verify pid is still alive on this host
            pid = running.get("pid")
            if pid:
                try:
                    os.kill(pid, 0)  # signal 0: no-op, raises if process dead
                except (ProcessLookupError, PermissionError):
                    crashed = True  # pid gone → crashed
            else:
                crashed = True  # no pid to check → assume crashed

    return {
        "state": "crashed" if crashed else state,
        "running": running,
        "latest_completed": latest,
    }


def check_llm_service() -> dict:
    """Ping TabbyAPI at :8200. Returns latency in ms or error."""
    import urllib.request
    import time

    url = os.environ.get("LLM_BASE_URL", "http://100.65.249.20:8200/v1") + "/models"
    try:
        t0 = time.monotonic()
        with urllib.request.urlopen(url, timeout=3) as resp:
            resp.read()
        latency_ms = round((time.monotonic() - t0) * 1000)
        return {"status": "ok", "latency_ms": latency_ms}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def check_advisor_report() -> dict:
    """Check if advisor latest.json exists and is not expired."""
    path = ADVISOR_DIR / "latest.json"
    if not path.exists():
        return {"status": "missing"}
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        expires_at = report.get("expires_at")
        if expires_at:
            exp = datetime.fromisoformat(expires_at)
            if datetime.now(timezone.utc) > exp:
                return {"status": "expired", "expired_at": expires_at}
        return {
            "status": "ok",
            "generated_at": report.get("generated_at"),
            "credit_tier": report.get("credit_tier"),
            "immediate_count": len(report.get("immediate", [])),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def main() -> int:
    quiet = "--quiet" in sys.argv

    db = check_database()
    pipeline = check_pipeline_state()
    llm = check_llm_service()
    advisor = check_advisor_report()

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "host": socket.gethostname(),
        "database": db,
        "pipeline": pipeline,
        "llm_service": llm,
        "advisor_report": advisor,
    }

    if not quiet:
        print(json.dumps(report, indent=2, default=str))

    # Determine exit code
    if db["status"] == "error":
        return 2  # critical: DB unreachable
    if pipeline["state"] == "crashed":
        return 2  # critical: pipeline crashed
    if llm["status"] == "error" or advisor["status"] in ("missing", "expired"):
        return 1  # degraded but not critical
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**How `local-agent` MCP at :8300 polls health:**

The `local-agent` MCP exposes a `bash` tool. The system prompt for opportunity-domain agents should include:

```
## Health Check

To verify system health before querying opportunities:
    python scripts/health_check.py

Exit 0 = healthy. Exit 1 = degraded (advisor stale, LLM slow). Exit 2 = critical (DB down, pipeline crashed).
Output is JSON — parse the 'pipeline.state' and 'database.opportunity_count' fields.
```

---

### Gap 4 — `query_opportunities.py` Must Be Importable, Not CLI-Only

**Problem:** `query_opportunities.py` is a CLI script. The `local-agent` MCP at :8300 and the `rag-knowledge-base` MCP at :8301 cannot import `search_opportunities` from it. The function exists only inside `if __name__ == "__main__"`. This violates action parity — an agent can't query what a user can query from the command line.

**Skill principle applied:** Action Parity. Whatever the CLI does, the agent must be able to achieve via a callable function. The fix is to pull the query logic into `opportunity_api.py` (already specified in Gap 1 as `search_opportunities()`) and reduce `query_opportunities.py` to a thin CLI shim that calls the importable function.

#### Refactored `query_opportunities.py` (thin CLI shim):

```python
#!/usr/bin/env python3
"""
CLI shim for semantic opportunity search.

The actual search logic lives in opportunity_api.search_opportunities().
This file is a CLI wrapper only — import from opportunity_api directly.

Exit codes:
    0   Results found and printed
    1   No results found for query
    2   Database connection error
    3   Usage error (bad arguments)
"""
import sys
import json

from config_db import get_pgvector_connection
from opportunity_api import search_opportunities


def _print_results(results: list[dict]) -> None:
    for i, opp in enumerate(results, 1):
        print(f"\n{i}. {opp['title']}")
        print(f"   {'─' * 50}")
        print(f"   Revenue: {opp.get('revenue_claim', 'N/A')}")
        print(f"   Automation Score: {opp.get('automation_score', 'N/A')}/100")
        print(f"   Legitimacy: {opp.get('legitimacy_score', 'N/A')}/100")
        print(f"   Investment: {opp.get('initial_investment', 'N/A')}")
        print(f"   Source: {opp.get('source', 'N/A')}")
        print(f"   URL: {opp.get('url', 'N/A')}")
        print(f"   Similarity: {opp.get('similarity', 0.0):.3f}")
    print("\n" + "=" * 60)


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: python query_opportunities.py 'your search query'\n"
            "       python query_opportunities.py 'passive income' --json\n"
            "       python query_opportunities.py 'AI tools' --min-score 70 --max-invest 500",
            file=sys.stderr,
        )
        return 3  # usage error

    # Parse simple flags
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if not a.startswith("--")]
    query = " ".join(a for a in args if not a.lstrip("-").isdigit())

    min_score = None
    max_invest = None
    for i, arg in enumerate(sys.argv):
        if arg == "--min-score" and i + 1 < len(sys.argv):
            min_score = int(sys.argv[i + 1])
        if arg == "--max-invest" and i + 1 < len(sys.argv):
            max_invest = float(sys.argv[i + 1])

    try:
        with get_pgvector_connection() as conn:
            results = search_opportunities(
                conn,
                query,
                limit=10,
                min_automation_score=min_score,
                max_investment_usd=max_invest,
            )
    except Exception as exc:
        print(f"Database error: {exc}", file=sys.stderr)
        return 2  # DB error

    if not results:
        print(f"No results found for: '{query}'", file=sys.stderr)
        return 1  # no results

    print(f"\nSearching for: '{query}' — {len(results)} results\n" + "=" * 60)

    if as_json:
        print(json.dumps(results, indent=2, default=str))
    else:
        _print_results(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

#### Should `query_opportunities.py` expose its function via the `rag-knowledge-base` MCP at :8301?

**Recommendation: No — but expose it via `local-agent` MCP at :8300 instead.**

The `rag-knowledge-base` MCP at :8301 is a general semantic search service (likely ChromaDB or a vector store with its own ingestion pipeline). Routing opportunity search through it would require re-ingesting all opportunities into a second vector store, creating a sync problem. The opportunities are already in pgvector with richer metadata (investment ranges, scores, CRUD history) that the rag-knowledge-base MCP cannot filter on.

The correct integration is:

- `rag-knowledge-base` MCP at :8301: used for **knowledge documents** (e.g., the credit assessment doc, CLAUDE.md, domain research). Let it do what it was designed for.
- `local-agent` MCP at :8300: used for **opportunity queries**. The ReAct agent at :8300 should have `opportunity_api.search_opportunities` available as a tool (either via a thin FastAPI wrapper or via direct Python import if the MCP server is co-located with the opportunity bot on the Xeon).

**Integration spec for `local-agent` MCP at :8300:**

The agent at :8300 needs these tools registered in its system prompt:

```
## Available Opportunity Tools

- search_opportunities(query, min_automation_score?, max_investment_usd?):
    Semantic search over pgvector. Returns list of opportunities with similarity scores.

- get_opportunity(doc_id):
    Exact lookup by UUID. Returns full opportunity record or null.

- list_opportunities(min_automation_score?, max_investment_usd?, source?, embedding_status?):
    Filtered list without semantic search. Use when you want score/investment filters
    without a natural language query.

- update_opportunity(doc_id, updates):
    Partial update. Use to mark opportunities 'pursued', update category, etc.
    Allowed fields: embedding_status, embedding_error, recommended_action, category.

- delete_opportunity(doc_id):
    Remove a fraudulent or deprecated opportunity.

- scrape_source(source_name):
    Trigger a single scraper ('reddit'|'hackernews'|'producthunt'|'indiehackers').
    Returns raw records. You must call store_opportunity() for each record you want to keep.

- store_opportunity(analyzed):
    Upsert one analyzed opportunity. Returns doc_id. Call after analyze_opportunity().
```

These tools are implemented in `opportunity_api.py`. The `local-agent` MCP at :8300 should wrap them via a lightweight FastAPI server on the Xeon, or expose them as MCP tool definitions if the MCP server supports Python tool injection.

---

### Gap 5 — `data/pipeline_context.md` Must Be JSON, Not Markdown

**Problem:** The plan specifies writing `data/pipeline_context.md` as Markdown. Markdown is not machine-readable. The `local-agent` at :8300 parsing this file must regex-scrape values from prose rather than deserializing a dict. The shared-workspace-architecture reference states: use conventions consistently; files consumed by both humans and agents should be structured data (JSON) with human-readable display handled at read time.

**Spec: `data/pipeline_context.json`**

```json
{
  "schema_version": 1,
  "last_run": {
    "completed_at": "2026-02-26T08:14:32.000Z",
    "sources_scraped": {
      "reddit": 42,
      "hackernews": 31,
      "producthunt": 28,
      "indiehackers": 19
    },
    "new_stored": 101,
    "cache_hits": 89,
    "skipped_duplicates": 67,
    "duration_seconds": 847
  },
  "database": {
    "backend": "pgvector",
    "host": "10.0.0.87",
    "port": 5432,
    "dbname": "opportunity_bot",
    "total_opportunities": 1847,
    "pending_embeddings": 12,
    "last_embedding_run_at": "2026-02-26T08:15:01.000Z"
  },
  "credit_profile": {
    "entity": "ISNBIZ, INCORPORATED",
    "personal_fico_min_bureau": 763,
    "sbss_score": 210,
    "risk_tier": "MODERATE",
    "last_refreshed_at": "2026-02-04T00:00:00.000Z"
  },
  "known_issues": [
    "Reddit public JSON: 6s delay per request (unauthenticated rate limit)",
    "Embedding backfill: 12 rows pending (run embeddings.py --backfill to fix)"
  ],
  "llm_service": {
    "base_url": "http://100.65.249.20:8200/v1",
    "model": "Qwen3-30B-A3B",
    "cache_path": "data/llm_cache.sqlite",
    "cache_entries": 234
  }
}
```

**Schema decisions:**

- `schema_version` integer lets agents detect stale context files written by older pipeline versions.
- `sources_scraped` is a dict (not a string) so agents can filter by source without parsing prose.
- `known_issues` is an array of strings — agents can iterate and surface them in reports.
- `pending_embeddings` is a count — agents can decide whether to trigger a backfill without a separate DB query.
- All timestamps are ISO 8601 UTC strings — `fromisoformat()` without string manipulation.

**Update in `production_opportunity_pipeline.py`:**

Replace the Markdown write with:

```python
import json
from pathlib import Path

def _update_pipeline_context(stats: dict, credit_profile=None) -> None:
    """
    Write data/pipeline_context.json with current pipeline state.
    Called at end of every successful run (before complete_pipeline_run()).
    """
    ctx_path = Path("data/pipeline_context.json")

    # Preserve fields that don't change per-run (credit profile, known issues)
    existing = {}
    if ctx_path.exists():
        try:
            existing = json.loads(ctx_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass  # corrupted — overwrite

    from config_db import get_pgvector_connection
    db_meta = {"backend": "pgvector", "host": "10.0.0.87", "port": 5432, "dbname": "opportunity_bot"}
    try:
        with get_pgvector_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*), COUNT(*) FILTER (WHERE embedding_status='pending') "
                "FROM business_opportunities"
            )
            total, pending = cur.fetchone()
            db_meta["total_opportunities"] = total
            db_meta["pending_embeddings"] = pending
    except Exception:
        db_meta["total_opportunities"] = existing.get("database", {}).get("total_opportunities")
        db_meta["pending_embeddings"] = None

    context = {
        "schema_version": 1,
        "last_run": {
            "completed_at": stats.get("completed_at"),
            "sources_scraped": stats.get("sources_scraped", {}),
            "new_stored": stats.get("new_stored", 0),
            "cache_hits": stats.get("cache_hits", 0),
            "skipped_duplicates": stats.get("skipped_duplicates", 0),
            "duration_seconds": stats.get("duration_seconds"),
        },
        "database": db_meta,
        "credit_profile": existing.get("credit_profile"),  # preserved from prior run
        "known_issues": stats.get("known_issues", []),
        "llm_service": {
            "base_url": os.environ.get("LLM_BASE_URL", "http://100.65.249.20:8200/v1"),
            "model": os.environ.get("LLM_MODEL", "Qwen3-30B-A3B"),
            "cache_path": "data/llm_cache.sqlite",
        },
    }

    ctx_path.write_text(json.dumps(context, indent=2, default=str), encoding="utf-8")
```

**Note on `data/pipeline_context.md`:** Delete the `.md` file. The JSON file replaces it entirely. Agents that need a human-readable summary can print `python -c "import json; d=json.load(open('data/pipeline_context.json')); print(d)"` or use `health_check.py` which includes the same data.

---

### Gap 6 — Exit-Code Convention for All CLI Tools

**Problem:** All CLI tools currently exit 0 on crash (Python's default on unhandled exception is exit 1, but the `try/except Exception: print(...)` pattern in the current scripts swallows the exception and exits 0). An orchestrator cannot distinguish "ran successfully" from "errored silently". The `local-agent` at :8300 calling any CLI tool via bash has no reliable signal.

**Skill principle applied:** Completion Signals. Agents need explicit, deterministic signals. Exit codes are the POSIX completion signal for CLI tools.

#### Exit-Code Table (all CLI tools)

| Exit Code | Meaning | When to use |
|-----------|---------|-------------|
| 0 | Success | Normal completion, output is valid |
| 1 | No results / empty output | Query returned 0 results; nothing to parse |
| 2 | Runtime error — recoverable | DB connection failed, LLM timeout, rate limit |
| 3 | Usage / argument error | Bad CLI arguments, missing required flag |
| 4 | Crash — unrecoverable | Unhandled exception, corrupted state, assertion failed |
| 5 | Partial completion | Multi-step run: some sources failed, some succeeded |

**Application per file:**

| CLI file | Current exit behavior | Corrected exit codes |
|---|---|---|
| `query_opportunities.py` | 0 always (exception swallowed) | 0=results, 1=no results, 2=DB error, 3=usage |
| `production_opportunity_pipeline.py` | 0 always | 0=all sources ok, 2=fatal DB error, 5=partial (some sources failed) |
| `personalized_opportunity_bot.py` | 0 always | 0=ok, 2=DB error, 4=profile not found (unrecoverable) |
| `credit_integration/advisor.py` (run_advisor) | n/a (not CLI) | 0=ok, 1=no opps found, 2=DB error |
| `scripts/health_check.py` (new) | n/a (new) | 0=healthy, 1=degraded, 2=critical |
| `scripts/setup_pgvector.py` (new) | n/a (new) | 0=schema ok, 2=DB error, 4=schema already exists wrong version |
| `list_automation_opportunities.py` | 0 always | 0=results, 1=no results, 2=DB error |
| `generate_trends_report.py` | 0 always | 0=report written, 2=DB error |
| `analyze_chromadb.py` | 0 always | 0=ok, 2=DB error (deprecated after W1 — remove) |

**Implementation pattern (apply to every CLI `main()`):**

```python
import sys

def main() -> int:
    try:
        # ... actual logic ...
        if not results:
            return 1  # no results — not an error, but caller should know
        # ... print results ...
        return 0
    except (psycopg2.OperationalError, psycopg2.DatabaseError) as exc:
        print(f"Database error: {exc}", file=sys.stderr)
        return 2
    except (ValueError, FileNotFoundError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 4
    except Exception as exc:
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 4

if __name__ == "__main__":
    sys.exit(main())
```

**Key change:** Every script must end with `sys.exit(main())`. The `try/except Exception: print(...)` pattern that swallows errors and returns `None` (exit 0) is replaced with typed exception handlers that return specific exit codes.

**`local-agent` at :8300 usage in system prompt:**

```
## Exit Code Semantics

When calling opportunity bot CLI tools via bash:
- Exit 0: Success, parse stdout
- Exit 1: No results found — adjust your query or filters
- Exit 2: Infrastructure error — check health_check.py before retrying
- Exit 3: You passed bad arguments — fix the command
- Exit 4: Unrecoverable error — do not retry automatically; surface to user
- Exit 5: Partial — some sources failed; results may be incomplete but are valid
```

---

### Updated Acceptance Criteria (Round 3 additions)

Append these to the existing Workstream 1 acceptance criteria:

- [ ] `opportunity_api.py` exists at project root with complete CRUD: `get_opportunity`, `list_opportunities`, `search_opportunities`, `store_opportunity`, `update_opportunity`, `delete_opportunity`, `scrape_source`, `analyze_opportunity`
- [ ] `search_opportunities()` is importable from `opportunity_api` (not buried in `query_opportunities.py`)
- [ ] `query_opportunities.py` is a thin CLI shim calling `opportunity_api.search_opportunities()`
- [ ] `query_opportunities.py` exits 0/1/2/3 per exit-code table
- [ ] `production_opportunity_pipeline.py` writes `reports/runs/running.json` at start with pid, host, stage
- [ ] `production_opportunity_pipeline.py` updates `running.json` stage field at each pipeline stage transition
- [ ] `complete_pipeline_run()` writes `reports/runs/latest.json` AND deletes `reports/runs/running.json`
- [ ] `running.json` and `latest.json` use atomic rename (tempfile + replace)
- [ ] `scripts/health_check.py` exits 0/1/2 and outputs JSON with database, pipeline, llm_service, advisor_report sections
- [ ] `health_check.py` detects crashed pipeline via pid liveness check + age > 2h heuristic
- [ ] `data/pipeline_context.json` (not `.md`) is written at end of every successful run
- [ ] `pipeline_context.json` has `schema_version`, `last_run`, `database`, `credit_profile`, `known_issues`, `llm_service` fields
- [ ] All CLI tools (`query_opportunities.py`, `production_opportunity_pipeline.py`, `personalized_opportunity_bot.py`, `list_automation_opportunities.py`) use `sys.exit(main())` pattern
- [ ] All CLI tools return typed exit codes per the exit-code table (no silent swallow of exceptions)
- [ ] `data/pipeline_context.md` deleted (replaced by `.json`)

### Updated Capability Map for `local-agent` MCP at :8300

| Agent request | How agent achieves it | Notes |
|---|---|---|
| "Search for passive income opportunities" | `search_opportunities(conn, "passive income")` via opportunity_api | semantic |
| "Find opps under $200" | `search_opportunities(conn, q, max_investment_usd=200)` | filtered semantic |
| "List all Reddit opportunities" | `list_opportunities(conn, source="reddit")` | filtered list |
| "Show me opportunity abc-def" | `get_opportunity(conn, "abc-def")` | exact lookup |
| "Mark opportunity as pursued" | `update_opportunity(conn, doc_id, {"category": "pursued"})` | partial update |
| "Delete the scam opportunity" | `delete_opportunity(conn, doc_id)` | requires doc_id |
| "Scrape fresh Reddit data" | `scrape_source("reddit")` → `analyze_opportunity` → `store_opportunity` | agent composes primitives |
| "Is the system healthy?" | `python scripts/health_check.py` via bash | exit code + JSON |
| "When did the pipeline last run?" | read `data/pipeline_context.json` | machine-readable |
| "Is the pipeline currently running?" | read `reports/runs/running.json` | tombstone pattern |
| "Run a fresh advisor report" | call `advisor.run_advisor(profile)` directly or trigger pipeline | requires credit profile |
| "What embedding failures exist?" | `list_opportunities(conn, embedding_status="failed")` | CRUD read |
| "Retry failed embeddings" | `list_opportunities(conn, embedding_status="failed")` → `update_opportunity(conn, id, {"embedding_status": "pending"})` | agent composes two primitives |

**CRUD completeness audit (post-Round-3):**

| Entity | Create | Read One | Read Many | Update | Delete |
|--------|--------|----------|-----------|--------|--------|
| `business_opportunities` | `store_opportunity` | `get_opportunity` | `list_opportunities` + `search_opportunities` | `update_opportunity` | `delete_opportunity` |
| `pipeline_run` (state) | `_write_running_state` | read `running.json` | read `latest.json` | `_write_running_state` (stage update) | deleted by `complete_pipeline_run` |
| `llm_cache` | `cache_analysis` | `get_cached_analysis` | (no list needed) | (version bump invalidates) | (no delete needed — TTL) |
| `credit_profile` | `_load_or_create_profile` | `FICOParser.load_profile` | (single profile per entity) | (reload from assessment doc) | (manual file deletion) |

All primary entities have full CRUD. No orphan create-only operations.
