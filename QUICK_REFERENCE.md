# ⚡ Quick Reference Card

## 🚀 **Common Commands**

### Start Your Session
```bash
source venv/bin/activate
```

### Run Scraping

**Demo Mode** (No API keys needed):
```bash
python3 production_opportunity_pipeline.py --demo
```

**Production Mode** (Requires Reddit API key):
```bash
python3 production_opportunity_pipeline.py
```

### Query Your RAG

```bash
# General search
python3 query_opportunities.py "high automation passive income"

# Filter by investment
python3 query_opportunities.py "under $1000 investment"

# Filter by difficulty
python3 query_opportunities.py "easy to build quick wins"

# Specific tech
python3 query_opportunities.py "Python AI automation"
```

### Check Status

```bash
# Database size
python3 -c "import chromadb; client = chromadb.PersistentClient(path='rag-business/chroma_db'); c = client.get_collection('business_opportunities'); print(f'Total: {c.count()} opportunities')"

# Qwen health
curl http://localhost:8080/health

# View latest log
tail -f logs/scraping_*.log
```

---

## 🔧 **Setup Commands**

### Initial Setup
```bash
# Create virtual environment & install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure API Keys
```bash
cp .env.example .env
nano .env  # Add your Reddit credentials
```

### Setup Automation
```bash
./setup_cron.sh  # Daily runs at 9 AM
```

---

## 📝 **API Keys**

### Reddit (Required)
1. Visit: https://www.reddit.com/prefs/apps
2. Create "script" app
3. Copy `client_id` and `client_secret`
4. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_id
   REDDIT_CLIENT_SECRET=your_secret
   ```

### Google (Optional)
1. Get key: https://developers.google.com/custom-search/v1/overview
2. Create CSE: https://cse.google.com/cse/all
3. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_key
   GOOGLE_CSE_ID=your_cse_id
   ```

---

## ⚙️ **Customization**

Edit `scrapers/config.py`:

```python
# Subreddits to monitor
REDDIT_SUBREDDITS = [
    "SideProject",
    "Entrepreneur",
    "YourNiche",  # Add yours
]

# Search queries
REDDIT_SEARCH_QUERIES = [
    "made $ revenue",
    "your custom query",
]

# Google dorks
GOOGLE_DORK_QUERIES = [
    'site:reddit.com "made $" automation',
    'your custom dork',
]

# Limits
MAX_OPPORTUNITIES_PER_SOURCE = 50
MIN_REVENUE_MENTION = 100
RATE_LIMIT_REDDIT = 30
```

---

## 📊 **Example Queries**

```bash
# High automation opportunities
python3 query_opportunities.py "automation score above 90"

# Passive income ideas
python3 query_opportunities.py "passive income automated"

# Low investment
python3 query_opportunities.py "under $500 startup cost"

# Quick wins
python3 query_opportunities.py "build in 1 week"

# Specific revenue
python3 query_opportunities.py "making $5000 per month"

# Tech-specific
python3 query_opportunities.py "AI GPT-4 automation"
```

---

## 🛠️ **Troubleshooting**

**Q: "No module named 'praw'"**
A: Activate venv: `source venv/bin/activate`

**Q: "Reddit API credentials missing"**
A: Get free credentials: https://www.reddit.com/prefs/apps

**Q: "LLM server not running"**
A: Start Qwen: `cd llama-cpp-docker && docker-compose up -d`

**Q: "No opportunities found"**
A: Use demo mode first: `--demo` flag

---

## 📁 **File Locations**

```
Configuration:
├── .env                          ← Your API keys
├── scrapers/config.py            ← Scraper settings
└── requirements.txt              ← Dependencies

Data:
├── rag-business/chroma_db/       ← RAG database
└── logs/                         ← Daily run logs

Scripts:
├── production_opportunity_pipeline.py  ← Main pipeline
├── query_opportunities.py              ← Search RAG
├── setup_cron.sh                       ← Automation
└── run_daily_scraping.sh              ← Cron wrapper

Docs:
├── RUN_ME_FIRST.md               ← Start here
├── QUICKSTART.md                 ← 5-min setup
├── README_PRODUCTION.md          ← Full guide
├── ARCHITECTURE.md               ← System design
└── QUICK_REFERENCE.md            ← This file
```

---

## ⏰ **Cron Management**

```bash
# View crontab
crontab -l

# Edit crontab
crontab -e

# Remove crontab
crontab -r

# Test daily script
bash run_daily_scraping.sh

# View logs
tail -f logs/scraping_*.log
ls -lh logs/
```

---

## 🔄 **Daily Workflow**

**Manual Run:**
```bash
source venv/bin/activate
python3 production_opportunity_pipeline.py
python3 query_opportunities.py "your search"
```

**Automated Run:**
```bash
# Runs daily at 9 AM via cron
# Check logs: tail -f logs/scraping_*.log
```

---

## 📈 **Performance**

- Scraping: ~10 min (80-150 opportunities)
- Analysis: ~10 sec/opportunity (Qwen)
- Total: ~15-20 min per run
- Storage: ~1MB per 100 opportunities

---

## 🎯 **Next Steps**

1. ✅ **Test**: `python3 production_opportunity_pipeline.py --demo`
2. ⏭️ **Setup**: Get Reddit API key
3. ⏭️ **Run**: `python3 production_opportunity_pipeline.py`
4. ⏭️ **Automate**: `./setup_cron.sh`
5. ⏭️ **Customize**: Edit `scrapers/config.py`

---

**Need help?** Check the full docs in `README_PRODUCTION.md`
