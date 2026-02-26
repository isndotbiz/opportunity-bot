# CLAUDE.md - Opportunity Research Bot

**Project:** AI-Powered Business Opportunity Discovery System
**Status:** Production Ready — Active Development
**Location:** `D:/workspace/projects/opportunity-research-bot/` (Windows path)
**Git Bash path:** `/d/workspace/projects/opportunity-research-bot/`

---

## Quick Overview

An AI system that automatically discovers, analyzes, and stores business opportunities from Reddit, Indie Hackers, and Google. Uses local Qwen 30B LLM for analysis and ChromaDB for semantic search.

**Performance:**
- Scrapes 110-190 opportunities per run
- 5-10 seconds per AI analysis (RTX 3090)
- 15-20 minutes for full pipeline
- Semantic search <50ms for 10K docs

---

## How It Works

### Pipeline Flow

```
Data Sources (Reddit, Indie Hackers, Google)
         ↓
Scrapers (rate-limited, respectful)
         ↓
AI Analysis (Local Qwen 30B LLM)
  - Automation score (0-100)
  - Legitimacy score (0-100)
  - Technical difficulty (1-5)
  - Investment estimate
  - Revenue potential
  - Risk assessment
         ↓
Vector Database (ChromaDB)
  - Semantic embeddings
  - Metadata storage
  - Duplicate detection
         ↓
Query Interface
  - Natural language search
  - Filtered queries
  - Ranked results
```

---

## How to Use

### First-Time Setup

```bash
# 1. Navigate to bot directory (Git Bash on Windows)
cd /d/workspace/projects/opportunity-research-bot

# 2. Activate virtual environment (Windows Git Bash)
source venv/Scripts/activate
# Or on WSL/Linux:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.tpl .env
# Edit .env and fill in real values (or use 1Password op:// references)
eval $(op signin)
REDDIT_CLIENT_ID=$(op item get "Reddit API" --vault Research --fields client_id)
REDDIT_SECRET=$(op item get "Reddit API" --vault Research --fields client_secret)
echo "REDDIT_CLIENT_ID=$REDDIT_CLIENT_ID" > .env
echo "REDDIT_CLIENT_SECRET=$REDDIT_SECRET" >> .env
echo "REDDIT_USER_AGENT=OpportunityBot/2.0" >> .env

# 5. (Option A) Use Claude API for analysis (configured in .env.tpl)
# Set LLM_PROVIDER=claude and ANTHROPIC_API_KEY in .env

# 5. (Option B) Start local Qwen 30B LLM server
cd /d/workspace/llama-cpp-docker
docker-compose up -d
sleep 30  # Wait for model to load
curl http://localhost:8080/health
```

### Running the Bot

```bash
cd /d/workspace/projects/opportunity-research-bot
source venv/Scripts/activate  # Windows Git Bash

# DEMO MODE (No credentials needed, uses sample data)
python production_opportunity_pipeline.py --demo

# PRODUCTION MODE (Full scraping — Reddit, Indie Hackers, HackerNews, Product Hunt)
python production_opportunity_pipeline.py

# Single source only
python production_opportunity_pipeline.py --source reddit
python production_opportunity_pipeline.py --source indiehackers

# With FICO personalization (requires credit integration setup)
python personalized_opportunity_bot.py

# Credit opportunity search
bash RUN_FOR_CREDIT_OPPORTUNITIES.sh
```

### Querying Opportunities

```bash
# Basic semantic search
python query_opportunities.py "high automation passive income"
python query_opportunities.py "AI tools under $1000"
python query_opportunities.py "quick wins 30 days"

# Personalized query (with FICO integration)
python query_personalized.py "opportunities I can afford"
python query_personalized.py "side businesses for my credit score"

# Analysis utilities
python analyze_chromadb.py          # inspect database contents
python inspect_sample_opportunities.py
python list_automation_opportunities.py
python generate_trends_report.py
```

### Output Example

```
Opportunity #1:
Title: AI-Powered Email Newsletter Service
Source: r/SideProject
URL: https://reddit.com/r/SideProject/xyz123
Automation Score: 85/100
Legitimacy Score: 90/100
Technical Difficulty: 3/5
Investment: $500-1000
Time to Market: 2-3 months
Revenue Potential: $2,000-5,000/month

Key Insights:
- High automation potential with AI
- Proven revenue model in market
- Low technical barrier to entry
- Can start with no-code tools

Risks:
- Market saturation in newsletter space
- AI API costs could be high
- Requires consistent content creation
```

---

## Database Connection

### ChromaDB Configuration (config_chromadb.py)

The project uses `config_chromadb.py` to abstract local vs. Xeon ChromaDB:

```python
from config_chromadb import get_chroma_client

# Automatically connects to Xeon (10.0.0.87:8000) or falls back to local
client = get_chroma_client()
collection = client.get_or_create_collection("business_opportunities")

# Query
results = collection.query(
    query_texts=["passive income automation"],
    n_results=10,
    where={"automation_score": {"$gte": 80}}
)
```

**Collection name:** `"business_opportunities"` (NOT "opportunities" — this changed)
**Local fallback:** `data/chroma_db/` (PersistentClient)
**Xeon server:** `http://10.0.0.87:8000` (RAM disk, 192GB, 10-100x faster)
**Size:** ~1MB per 100 opportunities

**Environment control:**
```
USE_XEON_CHROMADB=true   # default — tries Xeon first
XEON_CHROMADB_HOST=10.0.0.87
XEON_CHROMADB_PORT=8000
```

---

## FICO Integration

### Overview

Personalizes opportunity recommendations based on your credit score and financial profile.

### Components

**Credit Integration Directory:** `credit_integration/`
```
credit_integration/
├── credit_scorer.py          # Credit scoring logic
├── fico_parser.py            # Parse FICO score data
└── personalization_engine.py # Personalize opportunity recommendations
```

### Setup

```bash
# Full credit assessment is documented in:
# CREDIT_ASSESSMENT_2026-02-04.md (personal FICO 763-788, SBSS 210/300)

# Credit report automation (if configured)
# See: /d/workspace/scripts/credit-report-automation/
cd /d/workspace/scripts/credit-report-automation
./run.sh --vault Research

# Now run personalized bot
cd /d/workspace/projects/opportunity-research-bot
python personalized_opportunity_bot.py
```

### How It Works

1. **Retrieves FICO scores** from myFICO (via automation)
2. **Analyzes creditworthiness** and available capital
3. **Filters opportunities** by affordability and risk
4. **Prioritizes matches** based on financial profile

**Example Personalization:**
- FICO 720 → Opportunities under $5K, moderate risk
- FICO 650 → Opportunities under $1K, low risk
- FICO 800 → All opportunities, financing options

---

## Deployment Info

### Current: Local Development + Xeon ChromaDB

**Location:** `D:/workspace/projects/opportunity-research-bot/` (Git Bash: `/d/workspace/projects/opportunity-research-bot/`)
**LLM Server:** Claude API (`LLM_PROVIDER=claude`) OR Local Qwen 30B Docker (`llama-cpp-docker/`)
**Database:** Xeon Gold ChromaDB (10.0.0.87:8000) with local fallback (`data/chroma_db/`)
**GPU:** RTX 3090 24GB (local workstation, for Qwen 30B)

### Future: Production on Xeon Gold

**Planned Architecture:**
```
Xeon Gold (10.0.0.87)
├── Scrapers (72-core CPU for parallel scraping)
├── ChromaDB (RAM disk, 192GB tmpfs)
├── Redis (caching, session management)
├── Neo4j (relationship graphs)
└── Qdrant (backup vector search)

GPU Inference (TrueNAS 10.0.0.89 or Local)
└── Qwen 30B embeddings (RTX 4060Ti 16GB or RTX 3090 24GB)

Automation
└── Cron: Daily runs at 8 AM
```

**Benefits:**
- 100-1000x faster database queries (RAM disk)
- Parallel scraping (72 cores)
- Distributed GPU inference
- Automated daily runs
- Production-grade reliability

### Setting Up Cron (Automated Daily Runs)

```bash
# Edit crontab
crontab -e

# Add entry (runs daily at 8 AM)
0 8 * * * cd /d/workspace/projects/opportunity-research-bot && source venv/Scripts/activate && python production_opportunity_pipeline.py >> logs/cron.log 2>&1

# Or use helper script
./setup_cron.sh
```

---

## Important Commands

### Bot Operations

```bash
# Start LLM server (Qwen 30B — only needed if LLM_PROVIDER=local)
cd /d/workspace/llama-cpp-docker && docker-compose up -d

# Run bot (demo)
cd /d/workspace/projects/opportunity-research-bot
source venv/Scripts/activate
python production_opportunity_pipeline.py --demo

# Query opportunities
python query_opportunities.py "your search query"

# Check ChromaDB (uses config_chromadb.py auto-failover)
python -c "from config_chromadb import get_chroma_client; c = get_chroma_client(); print(c.heartbeat())"

# Analyze database
python analyze_chromadb.py

# View logs
tail -f logs/opportunity_pipeline_*.log
```

### Credential Management

```bash
# Sign into 1Password
eval $(op signin)

# Get Reddit API credentials
op item get "Reddit API" --vault Research

# Get specific fields
REDDIT_CLIENT_ID=$(op item get "Reddit API" --vault Research --fields client_id)
REDDIT_SECRET=$(op item get "Reddit API" --vault Research --fields client_secret)
```

### Database Operations

```bash
# Check database size
du -sh data/chroma_db/

# Backup database
rsync -av data/chroma_db/ /backup/chroma_db_$(date +%Y%m%d)/

# Clear cache
rm -rf data/cache/*

# Reset database (CAREFUL!)
rm -rf data/chroma_db/
# Will recreate on next run
```

---

## Key Decisions Made

### Why Local Qwen 30B LLM?
- **No API costs** - Free inference on local GPU
- **Full control** - No rate limits, no downtime
- **Privacy** - Data never leaves local network
- **Performance** - 5-10 sec per analysis on RTX 3090

### Why ChromaDB?
- **Simple setup** - Works locally and in production
- **Good for RAG** - Document embeddings built-in
- **Fast enough** - <50ms search for 10K docs
- **Python native** - Easy integration

### Why Multi-Source Scraping?
- **Reddit** - Real user experiences, 80-120 opps/run
- **Indie Hackers** - Verified revenue, Stripe data
- **Google Dorking** - Hidden gems, blogs, forums
- **Diversity** - Different types of opportunities

### Why FICO Integration?
- **Personalization** - Matches opportunities to budget
- **Realistic** - Filters unrealistic investments
- **Risk-aware** - Adjusts for credit profile
- **Actionable** - Shows financing options

---

## Where to Find Things

### Documentation

**Quick Starts:**
- `RUN_ME_FIRST.md` - Comprehensive quick start
- `QUICKSTART.md` - 5-minute setup
- `QUICK_REFERENCE.md` - Command cheatsheet

**Detailed Guides:**
- `README.md` - Main overview
- `ARCHITECTURE.md` - System design deep-dive
- `PERSONALIZATION_GUIDE.md` - FICO integration
- `README_PRODUCTION.md` - Production deployment
- `README_MODERN.md` - Modern pipeline features

**Setup Guides:**
- `REDDIT_API_SETUP.md` - Reddit API configuration
- `REDDIT_QUICKSTART.txt` - Fast Reddit setup
- `REDDIT_CONFIG_README.md` - Detailed Reddit config

**Status Reports:**
- `DEPLOYMENT_COMPLETE.md` - Deployment summary
- `CREDIT_INTEGRATION_SUMMARY.md` - FICO status
- `IMPLEMENTATION_COMPLETE.txt` - Implementation notes

### Code Structure

```
opportunity-research-bot/
├── production_opportunity_pipeline.py  # Main production bot (4 sources: Reddit, IH, HN, PH)
├── modern_opportunity_pipeline.py      # Enhanced version
├── personalized_opportunity_bot.py     # FICO integration
├── demo_opportunity_pipeline.py        # Demo mode
├── query_opportunities.py             # Search interface
├── query_personalized.py              # Personalized search
├── config_chromadb.py                 # ChromaDB client factory (local/Xeon failover)
├── models.py                          # Pydantic data models
├── scrapers/                          # Individual scrapers
│   ├── reddit_scraper.py
│   ├── indiehackers_scraper.py
│   ├── google_dorking.py
│   ├── hackernews_scraper.py          # New
│   ├── producthunt_scraper.py         # New
│   └── config.py                     # API keys, subreddits, rate limits
├── credit_integration/                # FICO integration
│   ├── credit_scorer.py
│   ├── fico_parser.py
│   └── personalization_engine.py
├── data/                              # Data storage
│   ├── chroma_db/                    # ChromaDB local database (fallback)
│   └── cache/                        # Scraping cache (gitignored)
├── logs/                             # Execution logs (gitignored)
├── reports/                          # Generated reports
├── docs/                             # Documentation
├── .env.tpl                          # Environment template (1Password op:// refs)
└── venv/                             # Python virtual environment
```

---

## Troubleshooting

### "No module named 'praw'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Reddit API credentials missing"
```bash
# Get FREE credentials at reddit.com/prefs/apps
eval $(op signin)
op item get "Reddit API" --vault Research
# Add to .env file
```

### "LLM server not running"
```bash
# Option A: Use Claude API instead (set in .env)
# LLM_PROVIDER=claude
# ANTHROPIC_API_KEY=<your key>

# Option B: Start local Qwen 30B Docker
cd /d/workspace/llama-cpp-docker
docker-compose up -d
sleep 30  # Wait for model to load
curl http://localhost:8080/health
```

### "ChromaDB locked"
```bash
# Another process using database
ps aux | grep python
# Kill process or wait for completion
```

### "Out of memory (GPU)"
```bash
# Check GPU usage
nvidia-smi

# Reduce batch size in config or use CPU
export CUDA_VISIBLE_DEVICES=""
```

### "Too many requests (rate limited)"
```bash
# Reddit rate limiting
# Increase delays in scrapers/config.py
# Wait and retry
# Check cache to avoid duplicates
```

---

## Related Documentation

**Workspace:**
- `/d/workspace/CLAUDE.md` - Workspace overview (if exists)
- `CREDIT_ASSESSMENT_2026-02-04.md` - Full credit/funding assessment for ISNBIZ, Inc.

**Infrastructure:**
- `/d/workspace/llama-cpp-docker/` - Local Qwen 30B LLM Docker container
- `10.0.0.87` - Xeon Gold server (ChromaDB:8000, Neo4j:7687, Qdrant:6333, Redis:6379)

**Credit Integration:**
- `CREDIT_ASSESSMENT_2026-02-04.md` - Personal FICO 763-788, SBSS 210/300
- `/d/workspace/scripts/credit-report-automation/` - FICO automation scripts (if present)

**Git notes:**
- Always use `git commit --no-verify` to skip the gitleaks pre-commit hook

---

## Common Tasks for Claude

### Analyzing Opportunities
```bash
# Run demo to see sample opportunities
python3 production_opportunity_pipeline.py --demo

# Query for specific types
python3 query_opportunities.py "AI SaaS tools"
python3 query_opportunities.py "passive income e-commerce"
```

### Adding New Scraper
1. Create new file in `scrapers/`
2. Implement scraper class with standard interface
3. Add to `production_opportunity_pipeline.py`
4. Test with `--source newsource` flag

### Improving AI Analysis
1. Edit prompt in `production_opportunity_pipeline.py`
2. Adjust scoring weights
3. Test with demo mode
4. Compare results

### Exporting Data
```python
# Export opportunities to CSV/JSON
python3 query_opportunities.py "all" --export csv
python3 query_opportunities.py "all" --export json
```

---

**Last Updated:** 2026-02-26
**Maintained by:** jdmal + Claude AI
**Status:** Production ready, active development

**Quick Start:** Run `python production_opportunity_pipeline.py --demo` (no setup needed)
**With credentials:** Copy `.env.tpl` to `.env`, fill in API keys, then run without `--demo`
