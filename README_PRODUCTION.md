# 🚀 Production Opportunity Research Bot

**AI-powered system that scrapes business opportunities from Reddit, Indie Hackers, and Google → Analyzes them with local Qwen LLM → Stores in semantic search RAG database**

---

## 🎯 Features

✅ **Real Multi-Source Scraping:**
- Reddit API (PRAW) - Multiple subreddits with intelligent filtering
- Indie Hackers - Products & interviews with revenue verification
- Google Dorking - Hidden opportunities via custom search queries

✅ **AI Analysis:**
- Local Qwen3-Coder-30B (18GB model, GPU accelerated)
- Scores: automation potential, legitimacy, difficulty, scalability
- Structured JSON output with insights & recommendations

✅ **Semantic Search RAG:**
- ChromaDB vector database
- Natural language queries
- Metadata filtering by revenue, automation score, source, etc.

✅ **Production Ready:**
- Automated daily runs (cron)
- Rate limiting & error handling
- Detailed logging
- Demo mode for testing

---

## 📋 Quick Start

### 1. Setup

```bash
# Install dependencies & configure
./setup_production.sh

# Edit API credentials
nano .env
```

### 2. Test with Demo Mode (No API Keys Required)

```bash
python3 production_opportunity_pipeline.py --demo
```

### 3. Production Run

```bash
# Make sure Qwen is running
cd llama-cpp-docker && docker-compose up -d

# Run scraping
python3 production_opportunity_pipeline.py
```

### 4. Query Opportunities

```bash
# Search the RAG
python3 query_opportunities.py "high automation low investment"
```

### 5. Automate Daily Runs

```bash
# Setup cron job (runs daily at 9 AM)
./setup_cron.sh
```

---

## 🔑 API Credentials Setup

### Reddit API (Required for Reddit scraping)

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" type
4. Note your `client_id` and `client_secret`
5. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_id_here
   REDDIT_CLIENT_SECRET=your_secret_here
   ```

### Google Custom Search API (Optional for dorking)

1. Get API Key: https://developers.google.com/custom-search/v1/overview
2. Create Custom Search Engine: https://cse.google.com/cse/all
3. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_key_here
   GOOGLE_CSE_ID=your_cse_id_here
   ```

**Note:** Without Google API, the scraper falls back to basic web scraping (less reliable).

---

## 📁 Project Structure

```
workspace/
├── scrapers/
│   ├── reddit_scraper.py          # Reddit API integration
│   ├── indiehackers_scraper.py    # Indie Hackers scraping
│   ├── google_dorking.py          # Google search queries
│   └── config.py                  # Settings & API keys
│
├── production_opportunity_pipeline.py  # Main pipeline
├── query_opportunities.py              # Query RAG database
│
├── llama-cpp-docker/              # Local Qwen LLM
│   └── docker-compose.yml
│
├── rag-business/                  # ChromaDB storage
│   └── chroma_db/
│
├── logs/                          # Daily run logs
│
├── setup_production.sh            # Install & configure
├── setup_cron.sh                  # Automate daily runs
├── requirements.txt               # Python dependencies
└── .env                           # Your API keys (create from .env.example)
```

---

## 🛠️ Configuration

Edit `scrapers/config.py` to customize:

### Subreddits to Monitor
```python
REDDIT_SUBREDDITS = [
    "SideProject",
    "EntrepreneurRideAlong",
    "Entrepreneur",
    "SweatyStartup",
    "SaaS",
    # Add more...
]
```

### Search Keywords
```python
REDDIT_SEARCH_QUERIES = [
    "made $ revenue",
    "earning $ per month",
    "MRR revenue",
    # Add custom queries...
]
```

### Google Dork Queries
```python
GOOGLE_DORK_QUERIES = [
    'site:reddit.com "made $" "per month" automation',
    'site:indiehackers.com "$" "MRR" "automation"',
    # Add advanced queries...
]
```

### Rate Limits
```python
RATE_LIMIT_REDDIT = 30   # Requests per minute
RATE_LIMIT_WEB = 10
MAX_OPPORTUNITIES_PER_SOURCE = 50
```

---

## 📊 Example Queries

```bash
# High automation opportunities
python3 query_opportunities.py "high automation score passive income"

# Low initial investment
python3 query_opportunities.py "under $1000 investment quick to build"

# Specific tech stack
python3 query_opportunities.py "Python API SaaS automated"

# Recent opportunities
python3 query_opportunities.py "discovered this week AI automation"
```

---

## 🤖 How It Works

### Pipeline Flow

```
1. SCRAPE
   ├─ Reddit API → Extract posts with revenue mentions
   ├─ Indie Hackers → Parse products & interviews
   └─ Google Dorks → Find hidden gems

2. ANALYZE (Qwen LLM)
   ├─ Automation Score (0-100)
   ├─ Technical Difficulty (1-5)
   ├─ Time to Market estimate
   ├─ Initial Investment estimate
   ├─ Legitimacy Score (0-100)
   ├─ Key Insights
   ├─ Automation Opportunities
   └─ Risk Assessment

3. STORE (RAG Database)
   ├─ ChromaDB vector embeddings
   ├─ Full-text + metadata
   └─ Semantic search enabled

4. QUERY
   └─ Natural language search
```

### Intelligence Features

- **Duplicate Detection:** Same URL won't be stored twice
- **Revenue Extraction:** Regex patterns find $ mentions
- **Tech Stack Detection:** Identifies frameworks/tools
- **Relevance Filtering:** Skips low-quality posts
- **Smart Ranking:** Results sorted by relevance + metadata

---

## 🔧 Maintenance

### View Logs
```bash
# Latest run
tail -f logs/scraping_*.log

# All logs
ls -lh logs/
```

### Clear Old Data
```bash
# Remove logs older than 30 days (automatic)
find logs/ -name "scraping_*.log" -mtime +30 -delete

# Reset RAG database
rm -rf rag-business/chroma_db
```

### Update Dependencies
```bash
pip3 install -r requirements.txt --upgrade
```

---

## 🐛 Troubleshooting

### "Reddit API credentials missing"
→ Get credentials from https://www.reddit.com/prefs/apps
→ Add to `.env` file

### "LLM server not running"
→ Start Qwen: `cd llama-cpp-docker && docker-compose up -d`
→ Check: `curl http://localhost:8080/health`

### "No opportunities found"
→ Try demo mode: `python3 production_opportunity_pipeline.py --demo`
→ Check API credentials in `.env`

### Web scraping blocked
→ Use official APIs (Reddit PRAW, Google CSE)
→ Increase rate limit delays in `config.py`

---

## 🚀 Advanced Usage

### Run Specific Scrapers Only

```python
from scrapers import RedditScraper

scraper = RedditScraper()
opps = scraper.scrape_subreddit('SideProject', limit=20)
```

### Custom Analysis Prompts

Edit `production_opportunity_pipeline.py` → `analyze_with_qwen()` function

### Export Data

```python
import chromadb

client = chromadb.PersistentClient(path="rag-business/chroma_db")
collection = client.get_collection("business_opportunities")

# Get all data
all_data = collection.get()
print(all_data['metadatas'])
```

---

## 📈 Performance

**Scraping Speed:**
- Reddit: ~30 requests/min → 50-100 opportunities/run
- Indie Hackers: ~10 pages/min → 20-30 opportunities/run
- Google Dorks: API = 100/day, Scraping = 5/min

**Analysis Speed:**
- Qwen (RTX 3090): ~5-10 seconds per opportunity
- Full pipeline (100 opportunities): ~15-20 minutes

**Storage:**
- ChromaDB: ~1MB per 100 opportunities
- Logs: ~500KB per daily run

---

## 🎓 Learning Resources

### Reddit API (PRAW)
- Docs: https://praw.readthedocs.io/
- Rate limits: https://github.com/reddit-archive/reddit/wiki/API

### Google Custom Search
- API Guide: https://developers.google.com/custom-search/v1/overview
- Dork Examples: https://gist.github.com/sundowndev/283efaddbcf896ab405488330d1bbc06

### ChromaDB
- Docs: https://docs.trychroma.com/
- Query Guide: https://docs.trychroma.com/usage-guide#querying-a-collection

---

## 📝 License

MIT License - Use for anything!

---

## 🙋 Support

Issues or questions? Check:
1. Logs: `logs/scraping_*.log`
2. API status: Reddit, Google CSE dashboards
3. Qwen health: `curl http://localhost:8080/health`

---

**Built with local AI - No OpenAI required! 🔥**
