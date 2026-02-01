# 🎯 START HERE - Production Opportunity Research Bot

## What You Just Got:

✅ **Real Reddit API scraping** (r/SideProject, r/Entrepreneur, r/SaaS, etc.)
✅ **Indie Hackers scraping** (verified products with Stripe revenue)
✅ **Google dorking** (finds hidden opportunities via search queries)
✅ **Local Qwen AI analysis** (18GB model scoring each opportunity)
✅ **Semantic RAG database** (ChromaDB for natural language search)
✅ **Automated daily runs** (cron job setup)

---

## 🚀 Quick Start (Choose One):

### Option A: Test with Demo Data (2 minutes)

```bash
# 1. Create virtual environment & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run demo pipeline (no API keys needed)
python production_opportunity_pipeline.py --demo

# 3. Query results
python query_opportunities.py "high automation passive income"
```

### Option B: Production Scraping (5 minutes)

```bash
# 1. Setup environment
source venv/bin/activate

# 2. Get Reddit API credentials (FREE)
#    Visit: https://www.reddit.com/prefs/apps
#    Create app → Copy client_id & client_secret

# 3. Configure
cp .env.example .env
nano .env  # Add your Reddit credentials

# 4. Start Qwen (if not running)
cd llama-cpp-docker && docker-compose up -d && cd ..

# 5. Run production scraping
python production_opportunity_pipeline.py

# 6. Query your data
python query_opportunities.py "low investment quick wins"
```

---

## 📁 What's in This System:

```
Production Scrapers:
├── scrapers/reddit_scraper.py       ← Real Reddit API (PRAW)
├── scrapers/indiehackers_scraper.py ← Web scraping
├── scrapers/google_dorking.py       ← Google Custom Search
└── scrapers/config.py               ← Your settings

Main Pipeline:
├── production_opportunity_pipeline.py  ← Full scraping pipeline
├── demo_opportunity_pipeline.py        ← Original demo version
└── query_opportunities.py              ← Search your RAG

Setup Scripts:
├── setup_venv.sh                    ← Create Python environment
├── setup_cron.sh                    ← Automate daily runs
└── .env.example                     ← API key template

Documentation:
├── README_PRODUCTION.md             ← Full documentation
├── QUICKSTART.md                    ← 5-minute guide
└── RUN_ME_FIRST.md                  ← This file!

Qwen LLM:
└── llama-cpp-docker/                ← Local AI (already running!)
```

---

## 🔑 API Keys You Need:

### Reddit (Required for Reddit scraping)
- **Where:** https://www.reddit.com/prefs/apps
- **Type:** Script application
- **Cost:** FREE (30 requests/minute)
- **Add to `.env`:**
  ```
  REDDIT_CLIENT_ID=your_id
  REDDIT_CLIENT_SECRET=your_secret
  ```

### Google Custom Search (Optional for dorking)
- **Where:** https://developers.google.com/custom-search/v1/overview
- **Type:** API key + Custom Search Engine ID
- **Cost:** FREE (100 queries/day)
- **Add to `.env`:**
  ```
  GOOGLE_API_KEY=your_key
  GOOGLE_CSE_ID=your_cse_id
  ```

**Without API keys:** Demo mode still works with sample data!

---

## 📊 What the Pipeline Does:

```
1. SCRAPE (10-15 minutes)
   ├─ Reddit: 50-100 opportunities
   ├─ Indie Hackers: 20-30 opportunities
   └─ Google: 10-20 opportunities

2. ANALYZE (with Qwen AI)
   ├─ Automation Score (0-100)
   ├─ Legitimacy Score (0-100)
   ├─ Technical Difficulty (1-5)
   ├─ Time to Market estimate
   ├─ Initial Investment estimate
   └─ Risks & Insights

3. STORE (ChromaDB RAG)
   └─ Semantic search database

4. QUERY
   └─ Natural language search
```

---

## 🎯 Example Output:

```bash
$ python production_opportunity_pipeline.py

🔴 REDDIT SCRAPING:
  📡 Scraping r/SideProject...
    ✅ Found 23 opportunities
  📡 Scraping r/Entrepreneur...
    ✅ Found 31 opportunities

💡 INDIE HACKERS SCRAPING:
  📡 Scraping products...
    ✅ Found 18 opportunities

🔍 GOOGLE DORKING:
  🔎 Searching: site:reddit.com "made $" automation
    ✅ Found 12 results

✅ Total: 84 opportunities

🤖 ANALYZING:
  [1/84] AI Email Newsletter - Automation: 92/100
  [2/84] Twitter Scheduler - Automation: 88/100
  ...

💾 STORED 84 opportunities in RAG

$ python query_opportunities.py "passive income under $1000"

📊 Top 3 Results:
1. Notion Template Marketplace
   Automation: 95/100 | Revenue: $2K/mo
   Investment: $200 | Time: 1 month

2. AI Email Curator Tool
   Automation: 92/100 | Revenue: $4K/mo
   Investment: $500 | Time: 6 weeks
```

---

## ⏰ Automate It:

Run scraping daily at 9 AM:

```bash
./setup_cron.sh

# Manually test the cron job
bash run_daily_scraping.sh

# Check logs
tail -f logs/scraping_*.log
```

---

## 🛠️ Customize It:

Edit `scrapers/config.py`:

```python
# Monitor different subreddits
REDDIT_SUBREDDITS = [
    "SideProject",
    "EntrepreneurRideAlong",
    "YourNiche",  # Add yours!
]

# Custom search queries
REDDIT_SEARCH_QUERIES = [
    "made $ revenue",
    "your custom query here",
]

# Advanced Google dorks
GOOGLE_DORK_QUERIES = [
    'site:reddit.com "made $" "per month" automation',
    'your custom dork here',
]
```

---

## ❓ Troubleshooting:

**Q: "No module named 'praw'"**
A: Activate venv first: `source venv/bin/activate`

**Q: "Reddit API credentials missing"**
A: Get them FREE at https://www.reddit.com/prefs/apps

**Q: "LLM server not running"**
A: Start Qwen: `cd llama-cpp-docker && docker-compose up -d`

**Q: No opportunities found**
A: Use `--demo` flag to test with sample data first

---

## 🎓 Learn More:

- **Full Docs:** `README_PRODUCTION.md`
- **Quick Guide:** `QUICKSTART.md`
- **Reddit API:** https://praw.readthedocs.io/
- **Google Dorking:** https://gist.github.com/sundowndev/283efaddbcf896ab405488330d1bbc06

---

## 🚀 Your First Command:

```bash
# Activate environment
source venv/bin/activate

# Test with demo mode (no setup needed!)
python production_opportunity_pipeline.py --demo

# Then query results
python query_opportunities.py "high automation"
```

**That's it! You're ready to find automated business opportunities with AI! 🎉**
