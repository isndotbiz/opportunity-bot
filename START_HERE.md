# 🎯 START HERE - Opportunity Research Bot

## ✅ System Organized & Ready!

Your opportunity research bot is now in its own organized folder with all paths configured correctly.

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Navigate to the bot folder
cd /mnt/d/workspace/opportunity-research-bot

# 2. Run demo mode (uses sample data)
venv/bin/python3 production_opportunity_pipeline.py --demo

# 3. Query your opportunities
venv/bin/python3 query_opportunities.py "high automation"
```

**That's it! Working immediately!** ✅

---

## 📁 New Organized Structure

```
opportunity-research-bot/
├── 📄 README.md                        ← Overview (read this!)
├── 📄 START_HERE.md                    ← This file
├── 📄 RUN_ME_FIRST.md                  ← Detailed guide
├── 📄 QUICK_REFERENCE.md               ← Commands cheatsheet
│
├── 🐍 production_opportunity_pipeline.py  ← Main pipeline
├── 🐍 query_opportunities.py              ← Search opportunities
├── 🐍 demo_opportunity_pipeline.py        ← Demo version
│
├── 📁 scrapers/                        ← Production scrapers
│   ├── reddit_scraper.py               → Reddit API
│   ├── indiehackers_scraper.py         → Web scraping
│   ├── google_dorking.py               → Google dorks
│   └── config.py                       → Your settings
│
├── 📁 data/                            ← All data here
│   ├── chroma_db/                      → RAG database (10 opps)
│   └── cache/                          → Scraper cache
│
├── 📁 logs/                            ← Daily run logs
├── 📁 venv/                            ← Python environment
│
├── 🔧 setup_cron.sh                    ← Daily automation
├── 📋 requirements.txt                 ← Dependencies
└── 🔑 .env.example                     ← API key template
```

---

## 💡 What Changed

**Before:** Files scattered across `/mnt/d/workspace/`
**Now:** Everything organized in `/mnt/d/workspace/opportunity-research-bot/`

**Updated:**
- ✅ All file paths use relative paths (portable!)
- ✅ RAG database moved to `data/chroma_db/`
- ✅ Logs in dedicated `logs/` folder
- ✅ Cache in `data/cache/`
- ✅ Clean, organized structure

---

## 🎯 Common Tasks

### Run Demo Mode
```bash
cd /mnt/d/workspace/opportunity-research-bot
venv/bin/python3 production_opportunity_pipeline.py --demo
```

### Query Opportunities
```bash
venv/bin/python3 query_opportunities.py "passive income under $1000"
venv/bin/python3 query_opportunities.py "high automation quick wins"
venv/bin/python3 query_opportunities.py "AI tools making money"
```

### Set Up Production (with Reddit API)
```bash
# 1. Get FREE Reddit API credentials
#    Visit: https://www.reddit.com/prefs/apps

# 2. Configure
cp .env.example .env
nano .env  # Add your credentials

# 3. Run production scraping
venv/bin/python3 production_opportunity_pipeline.py
```

### Automate Daily Runs
```bash
./setup_cron.sh
```

---

## 📊 Current Database

**Location:** `data/chroma_db/`
**Opportunities:** 10 stored
**Status:** ✅ Working

---

## 🔧 Helpful Aliases (Optional)

Add to your `~/.bashrc`:

```bash
# Opportunity Bot shortcuts
alias opp-bot='cd /mnt/d/workspace/opportunity-research-bot'
alias opp-run='cd /mnt/d/workspace/opportunity-research-bot && venv/bin/python3 production_opportunity_pipeline.py --demo'
alias opp-query='cd /mnt/d/workspace/opportunity-research-bot && venv/bin/python3 query_opportunities.py'
```

Then use:
```bash
opp-bot          # Navigate to bot
opp-run          # Run demo
opp-query "AI"   # Query opportunities
```

---

## 📚 Documentation

**Quick Reference:**
- `README.md` - Overview
- `START_HERE.md` - This file
- `QUICK_REFERENCE.md` - Command cheatsheet

**Detailed Guides:**
- `RUN_ME_FIRST.md` - Complete setup guide
- `README_PRODUCTION.md` - Full documentation
- `ARCHITECTURE.md` - System design

---

## ✅ System Status

- ✅ Folder organized
- ✅ Paths updated
- ✅ RAG database migrated (10 opportunities)
- ✅ Demo mode tested
- ✅ Query system working
- ✅ Documentation updated

---

## 🎉 You're All Set!

Everything is organized and ready to use. The system works exactly the same, just cleaner!

**Next:** Try querying your existing opportunities:
```bash
venv/bin/python3 query_opportunities.py "high automation"
```

---

**Need help?** Check `README.md` or `RUN_ME_FIRST.md`
