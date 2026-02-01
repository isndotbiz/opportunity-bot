# ⚡ Quick Start Guide - 5 Minutes to Production

## Option 1: Demo Mode (No Setup Required)

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run with demo data
python3 production_opportunity_pipeline.py --demo

# Query results
python3 query_opportunities.py "high automation"
```

✅ **Done!** You now have a working RAG with sample opportunities.

---

## Option 2: Production Mode (Real Scraping)

### Step 1: Get Reddit API Credentials (2 minutes)

1. Go to: https://www.reddit.com/prefs/apps
2. Click "Create App" → Choose "script"
3. Copy `client_id` (under app name) and `client_secret`

### Step 2: Configure

```bash
# Run setup
./setup_production.sh

# Edit .env file
nano .env

# Add your Reddit credentials:
REDDIT_CLIENT_ID=abc123...
REDDIT_CLIENT_SECRET=xyz789...
```

### Step 3: Start Qwen (if not running)

```bash
cd llama-cpp-docker
docker-compose up -d
cd ..
```

### Step 4: Run Production Scraping

```bash
python3 production_opportunity_pipeline.py
```

**First run:** Scrapes 50-100 real opportunities from Reddit, analyzes with Qwen, stores in RAG (~15-20 min)

### Step 5: Query Your Data

```bash
python3 query_opportunities.py "passive income under $1000"
```

---

## Option 3: Automate Daily Runs

```bash
# Setup cron job (runs every day at 9 AM)
./setup_cron.sh

# Check it's installed
crontab -l

# Monitor logs
tail -f logs/scraping_*.log
```

---

## 🎯 What You Get

After running the production pipeline:

```
✅ 50-100 real business opportunities
✅ AI analysis with scores & insights
✅ Semantic search RAG database
✅ Natural language queries
✅ Automated daily discovery
```

---

## 📊 Example Output

```
🔍 SCRAPING:
   Reddit: 78 opportunities
   Indie Hackers: 23 opportunities
   Google Dorks: 15 opportunities

🤖 ANALYZING:
   [1/116] AI Email Tool - Automation: 92/100
   [2/116] Twitter Scheduler - Automation: 88/100
   ...

💾 STORING:
   Stored 116 opportunities in RAG

🔎 QUERY: "high automation passive income"
   1. AI Email Newsletter - $4K/mo - Automation: 92/100
   2. Notion Template Marketplace - $2K/mo - Automation: 88/100
   3. Chrome Extension SaaS - $5K/mo - Automation: 85/100
```

---

## 🔧 Quick Commands Reference

```bash
# Test scraping (demo mode)
python3 production_opportunity_pipeline.py --demo

# Real scraping (needs API keys)
python3 production_opportunity_pipeline.py

# Query database
python3 query_opportunities.py "your search query"

# Check Qwen status
curl http://localhost:8080/health

# View logs
ls -lh logs/

# View stored opportunities
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='rag-business/chroma_db')
collection = client.get_collection('business_opportunities')
print(f'Total opportunities: {collection.count()}')
"
```

---

## ❓ Troubleshooting

**Q: "Reddit API credentials missing"**
A: Get credentials from https://www.reddit.com/prefs/apps and add to `.env`

**Q: "LLM server not running"**
A: Start Qwen: `cd llama-cpp-docker && docker-compose up -d`

**Q: "No opportunities found"**
A: Use `--demo` flag to test without API keys first

---

## 🚀 Next Steps

1. ✅ Run demo mode to test the system
2. ✅ Get Reddit API credentials
3. ✅ Run production scraping
4. ✅ Set up daily automation
5. ⭐ Customize scrapers/config.py for your niche
6. ⭐ Add more data sources (Twitter API, etc.)

---

**Ready? Start with:** `./setup_production.sh`
