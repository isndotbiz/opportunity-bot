# 🏗️ Production Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   OPPORTUNITY RESEARCH BOT                       │
│                  Production-Ready System                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   REDDIT     │  │INDIE HACKERS │  │    GOOGLE    │
│     API      │  │   SCRAPER    │  │   DORKING    │
│   (PRAW)     │  │  (BeautifulS)│  │ (Custom API) │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       └─────────────────┴──────────────────┘
                         │
                    [SCRAPERS]
                         │
                         ▼
       ┌─────────────────────────────────┐
       │   Raw Opportunities              │
       │   • Title, Description            │
       │   • Revenue claims                │
       │   • Tech stack mentions           │
       │   • Source URLs                   │
       └─────────────┬───────────────────┘
                     │
                     ▼
       ┌─────────────────────────────────┐
       │   QWEN AI ANALYSIS               │
       │   (18GB Local LLM)               │
       │                                   │
       │   • Automation Score (0-100)     │
       │   • Legitimacy Score (0-100)     │
       │   • Technical Difficulty (1-5)   │
       │   • Time to Market               │
       │   • Investment Estimate          │
       │   • Key Insights                 │
       │   • Risks & Opportunities        │
       └─────────────┬───────────────────┘
                     │
                     ▼
       ┌─────────────────────────────────┐
       │   CHROMADB (RAG)                 │
       │   Vector Database                │
       │                                   │
       │   • Semantic embeddings           │
       │   • Full-text search              │
       │   • Metadata filtering            │
       │   • Persistent storage            │
       └─────────────┬───────────────────┘
                     │
                     ▼
       ┌─────────────────────────────────┐
       │   QUERY INTERFACE                │
       │   Natural Language Search        │
       │                                   │
       │   "high automation under $1K"    │
       │   → Ranked, relevant results     │
       └──────────────────────────────────┘
```

---

## Data Flow

### 1. Scraping Phase

```python
Reddit API (PRAW)
├── Subreddits: SideProject, Entrepreneur, SaaS, etc.
├── Search queries: "made $", "MRR", "passive income"
├── Filters: Score > 50, revenue mentions, automation keywords
└── Output: ~50-100 opportunities

Indie Hackers Scraper
├── Products page (Stripe verified)
├── Interview posts
├── Revenue extraction from HTML
└── Output: ~20-30 opportunities

Google Dorking
├── Custom search queries
├── Site-specific: reddit.com, indiehackers.com
├── Advanced operators: "made $" "automation" "per month"
└── Output: ~10-20 opportunities

Total: 80-150 opportunities per run
```

### 2. Analysis Phase

```python
For each opportunity:
    ├── Extract context (title, description, revenue, tech)
    ├── Build analysis prompt
    ├── Call Qwen LLM (local, GPU-accelerated)
    │   ├── Temperature: 0.3 (consistent scoring)
    │   ├── Max tokens: 1000
    │   └── Format: Structured JSON
    ├── Parse JSON response
    │   ├── Automation score
    │   ├── Legitimacy score
    │   ├── Difficulty rating
    │   ├── Estimates (time, cost)
    │   └── Insights (opportunities, risks)
    └── Fallback on LLM failure

Average: 5-10 seconds per opportunity
Total: ~10-20 minutes for 100 opportunities
```

### 3. Storage Phase

```python
ChromaDB Persistent Client
├── Collection: "business_opportunities"
├── Documents: Markdown-formatted opportunity details
├── Embeddings: Auto-generated by ChromaDB
└── Metadata:
    ├── title: str
    ├── source: str
    ├── url: str
    ├── revenue_claim: str
    ├── automation_score: int (0-100)
    ├── legitimacy_score: int (0-100)
    ├── recommended_action: str (high/medium/low)
    ├── tech_stack: str
    ├── time_to_market: str
    ├── initial_investment: str
    └── created_at: ISO timestamp
```

### 4. Query Phase

```python
Natural Language Query
├── User input: "high automation passive income under $1K"
├── ChromaDB semantic search
│   ├── Vector similarity matching
│   ├── Metadata filtering
│   └── Relevance ranking
└── Results:
    ├── Top N opportunities
    ├── Sorted by similarity score
    └── Formatted with key metrics
```

---

## Component Details

### Scrapers

**reddit_scraper.py**
- **Technology:** PRAW (Python Reddit API Wrapper)
- **Rate Limits:** 30 requests/minute (Reddit API standard)
- **Features:**
  - Multi-subreddit searching
  - Keyword-based filtering
  - Revenue extraction (regex patterns)
  - Tech stack detection
  - Duplicate removal
- **Error Handling:** Graceful fallback on API errors

**indiehackers_scraper.py**
- **Technology:** BeautifulSoup4 + requests
- **Features:**
  - Products page scraping (Stripe-verified)
  - Interview parsing
  - Revenue pattern matching
  - Structured data extraction
- **Reliability:** HTML structure changes may require updates

**google_dorking.py**
- **Technology:** Google Custom Search API (or web scraping fallback)
- **Rate Limits:** 100 queries/day (free tier)
- **Features:**
  - Advanced search operators
  - Site-specific queries
  - Pattern-based filtering
  - Deduplication
- **Fallback:** Web scraping if API unavailable (less reliable)

### AI Analysis

**Qwen3-Coder-30B**
- **Model Size:** 18GB (GPU required)
- **Quantization:** 4-bit (GGUF format)
- **Hardware:** RTX 3090 (24GB VRAM)
- **Performance:** ~5-10 seconds per analysis
- **Prompting:** Structured JSON output with multiple scoring dimensions

**Analysis Dimensions:**
1. **Automation Score (0-100):** How automated is the opportunity?
2. **Legitimacy Score (0-100):** How credible is the revenue claim?
3. **Technical Difficulty (1-5):** How hard to implement?
4. **Time to Market:** Estimated build time
5. **Initial Investment:** Startup costs estimate
6. **Scalability (1-5):** Growth potential
7. **Key Insights:** 3-5 strategic points
8. **Automation Opportunities:** Specific areas to automate
9. **Risks:** Potential challenges

### RAG Database

**ChromaDB**
- **Type:** Persistent vector database
- **Storage:** Local filesystem (`rag-business/chroma_db/`)
- **Embeddings:** Auto-generated (default embedding function)
- **Features:**
  - Semantic search (vector similarity)
  - Metadata filtering
  - Full-text storage
  - Incremental updates

**Query Capabilities:**
```python
# Semantic search
collection.query(
    query_texts=["high automation"],
    n_results=10
)

# Metadata filtering
where={"automation_score": {"$gte": 80}}
where={"source": "Reddit r/SideProject"}

# Combined search
collection.query(
    query_texts=["passive income"],
    where={"automation_score": {"$gte": 80}},
    n_results=5
)
```

---

## Automation

### Cron Job Setup

**Daily Schedule:**
```cron
0 9 * * * /mnt/d/workspace/run_daily_scraping.sh
```

**Wrapper Script:**
```bash
run_daily_scraping.sh
├── Sets working directory
├── Loads environment variables (.env)
├── Runs production pipeline
├── Logs output (timestamped)
└── Cleans old logs (30+ days)
```

**Log Management:**
- Location: `logs/scraping_YYYY-MM-DD_HH-MM-SS.log`
- Retention: 30 days
- Auto-cleanup: Daily

---

## Configuration

### Environment Variables (.env)

```bash
# Reddit API
REDDIT_CLIENT_ID=abc123
REDDIT_CLIENT_SECRET=xyz789
REDDIT_USER_AGENT=OpportunityBot/1.0

# Google Custom Search
GOOGLE_API_KEY=your_key
GOOGLE_CSE_ID=your_cse_id
```

### Scraper Settings (scrapers/config.py)

```python
# Subreddits to monitor
REDDIT_SUBREDDITS = [...]

# Search queries
REDDIT_SEARCH_QUERIES = [...]

# Google dork patterns
GOOGLE_DORK_QUERIES = [...]

# Rate limits
RATE_LIMIT_REDDIT = 30  # per minute
RATE_LIMIT_WEB = 10
RATE_LIMIT_GOOGLE = 100

# Filters
MAX_OPPORTUNITIES_PER_SOURCE = 50
MIN_REVENUE_MENTION = 100  # dollars
```

---

## Error Handling

### Graceful Degradation

1. **Reddit API unavailable:**
   - Skip Reddit scraping
   - Continue with other sources
   - Log warning

2. **Qwen LLM offline:**
   - Use fallback analysis (conservative scores)
   - Mark as needing review
   - Continue pipeline

3. **ChromaDB error:**
   - Log detailed error
   - Skip storage for that opportunity
   - Continue with next opportunity

4. **Scraping failures:**
   - Retry logic (exponential backoff)
   - Skip problematic source
   - Continue with available data

### Monitoring

**Success Metrics:**
```python
stats = {
    'scraped': 0,      # Total opportunities found
    'analyzed': 0,     # Successfully analyzed
    'stored': 0,       # Stored in RAG
    'failed': 0        # Errors encountered
}
```

**Logs:**
- Daily run logs with timestamps
- Error messages with context
- Performance metrics (time per phase)

---

## Performance

### Benchmarks (RTX 3090)

| Phase | Time | Throughput |
|-------|------|------------|
| Reddit scraping | 3-5 min | 20-30 opps/min |
| Indie Hackers | 2-3 min | 10-15 opps/min |
| Google dorking | 1-2 min | 5-10 opps/min |
| Qwen analysis | 10-15 min | 6-10 opps/min |
| ChromaDB storage | 1-2 min | 50+ opps/min |
| **Total** | **15-25 min** | **80-150 opps/run** |

### Resource Usage

- **CPU:** Low (mostly I/O bound)
- **RAM:** ~2-4 GB (ChromaDB + Python)
- **GPU:** ~18 GB VRAM (Qwen model)
- **Disk:** ~1 MB per 100 opportunities
- **Network:** Minimal (API calls, ~10 MB/run)

---

## Security

### API Key Protection

- Keys stored in `.env` (gitignored)
- Never logged or exposed
- Environment variable loading
- Separate `.env.example` template

### Rate Limiting

- Respects API limits
- Exponential backoff on errors
- Sleep delays between requests
- Configurable limits per source

### Data Privacy

- No personal data collected
- Public posts only
- URLs preserved (attributions)
- Local storage (no cloud uploads)

---

## Extensibility

### Adding New Scrapers

```python
# 1. Create new scraper module
class NewSourceScraper:
    def scrape_all(self) -> List[Dict]:
        # Implementation
        return opportunities

# 2. Add to production pipeline
from scrapers.new_source import NewSourceScraper

new_scraper = NewSourceScraper()
new_opps = new_scraper.scrape_all()
all_opportunities.extend(new_opps)

# 3. Update config
NEW_SOURCE_SETTINGS = {...}
```

### Custom Analysis Prompts

Edit `production_opportunity_pipeline.py`:

```python
def analyze_with_qwen(self, opportunity):
    prompt = f"""
    Your custom analysis prompt here...
    Focus on: {your_custom_criteria}
    """
    # Rest of analysis logic
```

### Additional Metadata

Add fields to storage:

```python
metadatas=[{
    "title": opportunity['title'],
    # ... existing fields ...
    "custom_field": your_data,
    "another_field": more_data,
}]
```

---

**Built for production. Scales to thousands of opportunities. Local AI - no API costs! 🚀**
