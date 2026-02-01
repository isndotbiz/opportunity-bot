# Opportunity Research Bot - Project Overview

**Project:** AI-Powered Business Opportunity Discovery System
**Status:** Production Ready
**Type:** Python application with LLM integration
**Location:** `/mnt/d/workspace/opportunity-research-bot/`
**Last Updated:** 2026-02-01

---

## Purpose

Automated system that discovers, analyzes, and ranks business opportunities from multiple sources:
- **Scrapes:** Reddit, Indie Hackers, Google search results
- **Analyzes:** Local Qwen 30B LLM for opportunity evaluation
- **Stores:** ChromaDB vector database for semantic search
- **Personalizes:** FICO score integration for personalized recommendations

**Primary Goal:** Identify high-value passive income opportunities with automation potential.

---

## Quick Facts

**Technology Stack:**
- **Language:** Python 3.x
- **LLM:** Qwen 30B (local inference via llama.cpp)
- **Database:** ChromaDB (vector storage)
- **Scraping:** BeautifulSoup, Playwright, requests
- **APIs:** Reddit API, Google Custom Search API

**Performance:**
- **Scraping:** ~100-500 opportunities per run
- **Analysis:** ~5-10 seconds per opportunity
- **Storage:** 10,000+ opportunities indexed
- **Query:** <1 second semantic search

**Credentials:** All in 1Password (Reddit API, Google API)

---

## Directory Structure

```
opportunity-research-bot/
├── .serena/                          # Serena AI context
├── .git/                             # Git repository
├── venv/                             # Python virtual environment
│
├── CLAUDE.md                         # Claude quick reference
├── RUN_ME_FIRST.md                  # Getting started guide
├── QUICKSTART.md                    # Quick reference
├── README.md                        # Project documentation
│
├── production_opportunity_pipeline.py  # Main pipeline
├── query_opportunities.py            # Query interface
├── personalized_opportunity_bot.py   # FICO-aware version
│
├── scrapers/                         # Data collection
│   ├── reddit_scraper.py
│   ├── indie_hackers_scraper.py
│   └── google_scraper.py
│
├── analysis/                         # LLM analysis
│   ├── opportunity_analyzer.py
│   └── llm_client.py
│
├── storage/                          # Database
│   └── chroma_manager.py
│
├── data/                             # Local data
│   └── chroma_db/                   # ChromaDB storage
│
└── utils/                            # Utilities
    └── credential_manager.py         # 1Password integration
```

---

## How It Works

### 1. Data Collection (Scrapers)
```
Reddit → BeautifulSoup → Raw posts
Indie Hackers → Playwright → Project data
Google → Custom Search API → Articles
```

### 2. Analysis (LLM)
```
Qwen 30B evaluates:
- Automation potential (0-10)
- Passive income score (0-10)
- Market demand (0-10)
- Implementation difficulty (0-10)
- Overall viability (0-10)
```

### 3. Storage (ChromaDB)
```
Embeddings → Vector database
Metadata → Searchable fields
Full text → Preserved for context
```

### 4. Querying
```
Natural language query → Embedding
Semantic search → Top matches
Ranked results → JSON output
```

---

## Running the Bot

### Prerequisites

1. **Python Environment:**
   ```bash
   cd /mnt/d/workspace/opportunity-research-bot
   source venv/bin/activate
   ```

2. **LLM Server (Qwen 30B):**
   ```bash
   cd /mnt/d/workspace/llama-cpp-docker
   docker-compose up -d
   # Verify: curl http://localhost:8080/health
   ```

3. **Credentials (1Password):**
   ```bash
   eval $(op signin)
   # Reddit API, Google API automatically retrieved
   ```

### Demo Mode (No Credentials Needed)

```bash
cd /mnt/d/workspace/opportunity-research-bot
python3 production_opportunity_pipeline.py --demo
```

**What demo mode does:**
- Uses sample data (no API calls)
- Runs full analysis pipeline
- Stores in ChromaDB
- Perfect for testing

### Production Mode

```bash
cd /mnt/d/workspace/opportunity-research-bot
python3 production_opportunity_pipeline.py

# With custom parameters
python3 production_opportunity_pipeline.py \
  --max-results 100 \
  --min-score 7.0 \
  --sources reddit,indie_hackers
```

### Query Opportunities

```bash
# Basic query
python3 query_opportunities.py "high automation passive income"

# With filters
python3 query_opportunities.py "SaaS ideas" --min-score 8.0 --limit 10

# FICO-personalized (requires credit score)
python3 personalized_opportunity_bot.py
```

---

## Configuration

### Environment Variables (Optional)

Create `.env` file (excluded from git):
```bash
# Reddit API
REDDIT_CLIENT_ID=auto_from_1password
REDDIT_CLIENT_SECRET=auto_from_1password

# Google API
GOOGLE_API_KEY=auto_from_1password
GOOGLE_CSE_ID=auto_from_1password

# LLM Server
LLM_ENDPOINT=http://localhost:8080

# ChromaDB
CHROMA_PATH=./data/chroma_db
```

**Default behavior:** All credentials auto-retrieved from 1Password.

### 1Password Credential Locations

**Vault:** `Research` or `Development`

**Items:**
- `Reddit API` - client_id, client_secret
- `Google Custom Search API` - api_key, cse_id
- `FICO Credentials` - (if using personalized mode)

---

## LLM Integration

### Local Qwen 30B Server

**Why local LLM?**
- No API costs (OpenAI GPT-4 = $$$)
- Full privacy (data stays local)
- Customizable (fine-tune for our use case)
- Fast (local GPU inference)

**Model Details:**
- **Model:** Qwen 30B quantized (Q4_K_M)
- **Size:** ~18 GB
- **Context:** 32K tokens
- **Speed:** ~5-10 tokens/sec on RTX 3090

**Starting the Server:**
```bash
cd /mnt/d/workspace/llama-cpp-docker
docker-compose up -d

# Check status
docker-compose logs -f

# Stop when done
docker-compose down
```

**API Endpoint:** `http://localhost:8080/v1/chat/completions`

---

## ChromaDB Storage

### Database Structure

**Collection:** `business_opportunities`

**Documents:** Opportunity descriptions
**Embeddings:** Semantic vectors (384-dim)
**Metadata:**
- `source` - reddit/indie_hackers/google
- `automation_score` - 0-10
- `passive_income_score` - 0-10
- `overall_score` - 0-10
- `date_scraped` - ISO timestamp
- `url` - Source URL
- `title` - Opportunity title

### Database Location

**Current:** `/mnt/d/workspace/opportunity-research-bot/data/chroma_db/`
- File-based SQLite storage
- Embedded in application
- Works fine for development

**Future (Optional):** ChromaDB server on Xeon Gold
- `http://10.0.0.87:8000`
- Shared across applications
- Better for production scale

### Querying the Database

```python
from storage.chroma_manager import ChromaManager

# Initialize
chroma = ChromaManager()

# Query
results = chroma.query(
    query_text="high automation low investment",
    n_results=10,
    min_score=7.0
)

# Filter by source
results = chroma.query(
    query_text="SaaS ideas",
    where={"source": "reddit"}
)
```

---

## FICO Integration

### Personalized Recommendations

The `personalized_opportunity_bot.py` adjusts recommendations based on:
- **Credit Score:** Higher score → higher capital opportunities
- **Business Credit:** Nav, Equifax Business scores
- **Risk Tolerance:** Derived from credit history
- **Available Capital:** Estimated from credit lines

**Example:**
```bash
python3 personalized_opportunity_bot.py

# Retrieves:
# - myFICO score (personal credit)
# - Nav score (business credit)
# - Equifax Business score
# - Available credit lines

# Filters opportunities:
# - Low FICO → Low capital, proven models
# - High FICO → VC-backed, capital-intensive
```

**Credentials:** `Research` vault in 1Password

---

## Scrapers Detail

### Reddit Scraper
- **Subreddits:** r/SideProject, r/EntrepreneurRideAlong, r/Startup_Ideas
- **Filters:** Min upvotes, min comments, recency
- **Rate Limit:** Respects Reddit API limits
- **Output:** JSON with post content, metadata

### Indie Hackers Scraper
- **Source:** IndieHackers.com trending projects
- **Method:** Playwright (JavaScript rendering)
- **Data:** Project descriptions, revenue, MRR
- **Output:** Structured JSON

### Google Scraper
- **Query:** Custom search for business opportunity keywords
- **API:** Google Custom Search JSON API
- **Limit:** 100 queries/day (free tier)
- **Output:** Article titles, snippets, URLs

---

## Production Deployment

### Automated Runs (Cron)

```bash
# Daily at 6 AM
0 6 * * * cd /mnt/d/workspace/opportunity-research-bot && /usr/bin/python3 production_opportunity_pipeline.py >> /var/log/opportunity-bot.log 2>&1

# Weekly full scrape (Sundays at 2 AM)
0 2 * * 0 cd /mnt/d/workspace/opportunity-research-bot && /usr/bin/python3 production_opportunity_pipeline.py --max-results 1000 >> /var/log/opportunity-bot-weekly.log 2>&1
```

### Monitoring

**Logs:**
- Application logs: `./logs/opportunity_bot.log`
- Error logs: `./logs/errors.log`
- Scraper logs: `./logs/scrapers.log`

**Alerts:** (TODO)
- Email on scraper failures
- Slack notification for high-scoring opportunities
- Weekly summary report

---

## Development Workflow

### Making Changes

1. **Activate virtual environment:**
   ```bash
   cd /mnt/d/workspace/opportunity-research-bot
   source venv/bin/activate
   ```

2. **Make changes to code**

3. **Test:**
   ```bash
   # Test in demo mode first
   python3 production_opportunity_pipeline.py --demo

   # Then test with real APIs
   python3 production_opportunity_pipeline.py --max-results 10
   ```

4. **Commit to git:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```

### Adding New Scrapers

1. Create scraper file in `scrapers/`
2. Implement `scrape()` function
3. Return standardized JSON format
4. Add to `production_opportunity_pipeline.py`
5. Test with `--demo` mode
6. Document in README

---

## Git Repository

**Remote:** https://github.com/isndotbiz/opportunity-bot.git

**Branches:**
- `main` - Production-ready code
- `dev` - Development branch
- Feature branches for major changes

**Workflow:**
```bash
cd /mnt/d/workspace/opportunity-research-bot

# Status
git status

# Commit changes
git add .
git commit -m "Add new scraper for ProductHunt"
git push

# Pull latest
git pull origin main
```

---

## Performance Optimization

### Current Performance Bottlenecks

1. **LLM Analysis:** ~5-10 sec per opportunity
   - **Solution:** Batch processing, parallel requests

2. **Scraping Speed:** Rate-limited by APIs
   - **Solution:** Respect limits, run less frequently

3. **ChromaDB Writes:** Sequential writes slow
   - **Solution:** Batch upserts

### Future Optimizations

1. **Move ChromaDB to Xeon Gold:**
   - Network storage on fast server
   - Shared across instances
   - Better performance with RAM disk

2. **Parallel LLM Analysis:**
   - Multiple inference workers
   - Queue-based processing
   - GPU utilization increase

3. **Distributed Scraping:**
   - Multiple machines
   - Proxy rotation
   - Faster data collection

---

## Integration with Workspace

**One of 3 major projects:**
```
/mnt/d/workspace/
├── HROC_Files/              ← Non-profit website
├── ISNBIZ_Files/            ← Company website
└── opportunity-research-bot/ ← This project
```

**Shared Resources:**
- **LLM Server:** `/mnt/d/workspace/llama-cpp-docker/`
- **Credentials:** 1Password CLI (shared access)
- **Infrastructure:** Xeon Gold available for ChromaDB server

**Independent:**
- Own git repository
- Own virtual environment
- Own data storage
- Own documentation

---

## Credentials & Security

**All credentials in 1Password:**
```bash
eval $(op signin)

# Reddit API
op item get "Reddit API" --vault Research

# Google API
op item get "Google Custom Search API" --vault Research

# FICO credentials
op item get "myFICO" --vault Research
```

**NEVER hardcode credentials** - Always use 1Password CLI.

**Security practices:**
- `.env` excluded from git (`.gitignore`)
- API keys rotated regularly
- Rate limits respected
- No sensitive data in logs

---

## Next Steps & Priorities

### Short Term
1. **Improve LLM prompts** - Better opportunity scoring
2. **Add ProductHunt scraper** - Another data source
3. **Email alerts** - High-score opportunities
4. **Weekly reports** - Summary emails

### Medium Term
1. **Move ChromaDB to Xeon Gold** - Better performance
2. **Web UI** - Browse opportunities in browser
3. **API endpoint** - REST API for queries
4. **Slack integration** - Post opportunities to Slack

### Long Term
1. **Fine-tune Qwen model** - Domain-specific training
2. **Automated validation** - Verify opportunity viability
3. **Investment tracking** - Track which opportunities you pursue
4. **ROI measurement** - Measure actual returns

---

## Performance Notes

### Running from Windows Filesystem (Current)
**Location:** `/mnt/d/workspace/opportunity-research-bot/`
**Performance:** Adequate for current use
**Issue:** ChromaDB writes can be slow

### Running from Linux Filesystem (Recommended)
**Location:** `/home/jdmal/workspace/opportunity-research-bot/`
**Performance:** Much faster I/O (especially ChromaDB)
**Migration:**
```bash
rsync -av /mnt/d/workspace/opportunity-research-bot/ \
          /home/jdmal/workspace/opportunity-research-bot/

cd /home/jdmal/workspace/opportunity-research-bot
source venv/bin/activate
```

For production use, **strongly recommend ext4 filesystem** for better ChromaDB performance.

---

## Support & References

### Internal Documentation
- `RUN_ME_FIRST.md` - Getting started guide
- `QUICKSTART.md` - Quick reference
- `CLAUDE.md` - Claude AI assistance guide
- `.serena/` - This directory (Serena context)

### External Resources
- **ChromaDB:** https://docs.trychroma.com/
- **Reddit API:** https://www.reddit.com/dev/api/
- **Qwen Model:** https://huggingface.co/Qwen
- **llama.cpp:** https://github.com/ggerganov/llama.cpp

---

**Maintained by:** jdmal + Serena AI
**Review schedule:** Update monthly or when major changes occur
**Purpose:** Enable Serena to provide context-aware assistance for opportunity bot
**Status:** ✅ Production ready - running and discovering opportunities
