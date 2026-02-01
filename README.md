# 🤖 Opportunity Research Bot

**AI-powered system that discovers, analyzes, and stores business opportunities**

Scrapes opportunities from Reddit, Indie Hackers, and Google → Analyzes with local Qwen LLM → Stores in semantic search RAG database

---

## ⚡ Quick Start

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Test with demo data (no API keys needed)
python3 production_opportunity_pipeline.py --demo

# 3. Query opportunities
python3 query_opportunities.py "high automation passive income"
```

**That's it! The system is ready to use!** ✅

---

## 📁 What's Inside

```
opportunity-research-bot/
├── production_opportunity_pipeline.py  ← Main scraping pipeline
├── query_opportunities.py              ← Search your opportunities
├── demo_opportunity_pipeline.py        ← Demo version
│
├── scrapers/                           ← Production scrapers
│   ├── reddit_scraper.py               → Reddit API (PRAW)
│   ├── indiehackers_scraper.py         → Web scraping
│   ├── google_dorking.py               → Google dorks
│   └── config.py                       → Your settings
│
├── data/                               ← Data storage
│   ├── chroma_db/                      → RAG database
│   └── cache/                          → Scraper cache
│
├── logs/                               ← Daily run logs
├── venv/                               ← Python environment
│
├── setup_cron.sh                       ← Daily automation
├── requirements.txt                    ← Dependencies
└── .env.example                        ← API key template
```

---

## 📚 Documentation

**Start Here:**
- **RUN_ME_FIRST.md** - Complete quick start guide
- **QUICKSTART.md** - 5-minute setup
- **QUICK_REFERENCE.md** - Command cheatsheet

**Learn More:**
- **README_PRODUCTION.md** - Full documentation
- **ARCHITECTURE.md** - System design & internals
- **SUMMARY.txt** - Feature overview

---

## 🚀 Features

✅ **Multi-Source Scraping**
- Reddit API (PRAW) - 7+ subreddits
- Indie Hackers - Stripe-verified products
- Google Dorking - Hidden opportunities

✅ **AI Analysis**
- Local Qwen 30B (18GB, GPU accelerated)
- Automation scoring (0-100)
- Legitimacy assessment
- Investment estimates
- Risk analysis

✅ **Semantic Search RAG**
- ChromaDB vector database
- Natural language queries
- Metadata filtering

✅ **Production Ready**
- Automated daily runs (cron)
- Rate limiting & error handling
- Comprehensive logging
- Demo mode for testing

---

## 🔑 Setup (Optional)

### Demo Mode (No Setup)
Works immediately with sample data - perfect for testing!

### Production Mode
1. Get **FREE** Reddit API credentials:
   - Visit: https://www.reddit.com/prefs/apps
   - Create "script" app
   - Copy `client_id` and `client_secret`

2. Configure:
   ```bash
   cp .env.example .env
   nano .env  # Add your credentials
   ```

3. Run production scraping:
   ```bash
   python3 production_opportunity_pipeline.py
   ```

---

## 📊 Example Usage

```bash
# Run scraping pipeline
python3 production_opportunity_pipeline.py

# Query for specific opportunities
python3 query_opportunities.py "high automation under $1000"
python3 query_opportunities.py "passive income quick wins"
python3 query_opportunities.py "AI tools making money"

# Set up daily automation
./setup_cron.sh
```

---

## 🛠️ Customization

Edit `scrapers/config.py` to customize:
- Subreddits to monitor
- Search keywords
- Google dork queries
- Rate limits
- Result filters

---

## 📈 Performance

- **Scraping:** 80-150 opportunities per run
- **Analysis:** 5-10 sec/opportunity (Qwen on RTX 3090)
- **Total Time:** ~15-20 minutes
- **Storage:** ~1MB per 100 opportunities

---

## 🎯 What You Get

Each opportunity includes:
- Title & description
- Revenue claims (extracted)
- Tech stack (detected)
- Source URL
- **AI Analysis:**
  - Automation score (0-100)
  - Legitimacy score (0-100)
  - Technical difficulty (1-5)
  - Time to market estimate
  - Initial investment estimate
  - Key insights & opportunities
  - Risk assessment

---

## ❓ Troubleshooting

**Q: "No module named 'praw'"**
A: Activate venv: `source venv/bin/activate`

**Q: "Reddit API credentials missing"**
A: Get free credentials at https://www.reddit.com/prefs/apps

**Q: "LLM server not running"**
A: Start Qwen: `cd ../llama-cpp-docker && docker-compose up -d`

---

## 📝 License

MIT License - Use freely!

---

**Built with local AI - No API costs! 🔥**

For detailed documentation, see **RUN_ME_FIRST.md**
