# ⚡ IMMEDIATE RECOVERY ACTIONS

**Priority:** 🔴 CRITICAL - Prevent Data Loss & Consolidate

---

## 🎯 WHAT WE FOUND (So Far)

### ✅ GOOD NEWS - Data Still Exists!

**JSONL API Optimization Files:**
```
llama-cpp-docker/rag-output/
├── docs_n8n_io.jsonl          ← n8n workflows
├── docs_pydantic_dev.jsonl    ← Pydantic validation
├── platform_openai_com.jsonl  ← OpenAI API docs
├── platform_claude_com.jsonl  ← Claude API docs
├── docs_mistral_ai.jsonl      ← Mistral AI
└── 9+ more service docs...
```
**Purpose:** Optimized API documentation for LLMs to use services efficiently

**Docker Containers RUNNING:**
```
✅ rag-chromadb (port 8000) ← MAY CONTAIN YOUR BIG DATABASE!
✅ open-webui (port 3000)
⏸️  llama-qwen3 (exited but volumes may exist)
```

**Projects Found:**
```
✅ /mnt/d/workspace/projects/passive_income ← ORIGINAL PROJECT!
✅ /mnt/d/workspace/opportunity-research-bot ← NEW ORGANIZED
✅ /mnt/d/workspace/llama-cpp-docker/ ← JSONL docs
```

**Agents Currently Investigating:**
- 🔍 Passive income project structure & SQLite data
- 🐳 Docker rag-chromadb container (might have GB of data!)
- 💾 All ChromaDB databases
- 🏢 C-Corp/isn.biz/GitHub projects

---

## 🚨 IMMEDIATE PRIORITY ACTIONS

### 1. CHECK DOCKER RAG DATABASE (CRITICAL!)
**This might be where your GB of data is!**

```bash
# Check what's in the running ChromaDB container
curl http://localhost:8000/api/v1/heartbeat
curl http://localhost:8000/api/v1/collections

# List all collections and their sizes
python3 << 'EOF'
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
collections = client.list_collections()
for col in collections:
    print(f"{col.name}: {col.count()} items")
    data = col.get(limit=1)
    if data['metadatas']:
        print(f"  Sample fields: {list(data['metadatas'][0].keys())}")
EOF
```

### 2. BACKUP EVERYTHING NOW (Before Consolidation)
```bash
# Create timestamped backup
BACKUP_DIR="/mnt/d/workspace/CRITICAL_BACKUP_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup all RAG databases
cp -r /mnt/d/workspace/rag-business/chroma_db "$BACKUP_DIR/rag-business_backup"
cp -r /mnt/d/workspace/opportunity-research-bot/data/chroma_db "$BACKUP_DIR/opportunity-bot_backup"

# Backup passive_income project
cp -r /mnt/d/workspace/projects/passive_income "$BACKUP_DIR/passive_income_backup"

# Export Docker chromadb (if it has data)
docker exec rag-chromadb tar czf /tmp/chromadb_backup.tar.gz /chroma/chroma
docker cp rag-chromadb:/tmp/chromadb_backup.tar.gz "$BACKUP_DIR/"

# Backup JSONL files
cp -r /mnt/d/workspace/llama-cpp-docker/rag-output "$BACKUP_DIR/jsonl_docs_backup"

echo "✅ Backup complete: $BACKUP_DIR"
```

### 3. ANALYZE PASSIVE_INCOME PROJECT
```bash
cd /mnt/d/workspace/projects/passive_income

# What's in there?
ls -lah

# Find SQLite databases
find . -name "*.db" -o -name "*.sqlite*"

# Check for Python scripts
ls *.py

# Look for config/data files
ls *.json *.yaml *.env 2>/dev/null
```

### 4. CHECK TRUE_NAS BACKUPS
```bash
# Investigate January 9th backup
ls -lah /mnt/d/workspace/projects/True_Nas/backup-20260109/ai-configs/

# Check if n8n workflows are there
ls -lah /mnt/d/workspace/projects/True_Nas/backup-20260109/ai-configs/n8n/

# Check flowise data
ls -lah /mnt/d/workspace/projects/True_Nas/backup-20260109/ai-configs/flowise/
```

---

## 📊 CONSOLIDATION PLAN (After Agents Complete)

### Step 1: Merge All Opportunity Data
**Target:** Single unified `opportunity-research-bot/data/master_db/`

**Sources to merge:**
1. Docker rag-chromadb (port 8000) - might be HUGE!
2. /mnt/d/workspace/rag-business/chroma_db (472K - 8 opps)
3. opportunity-research-bot/data/chroma_db (504K - 10 opps)
4. passive_income SQLite data
5. Any data from True_Nas backups

### Step 2: Add Personalization Layer
**Create:** `user_profile.json`
```json
{
  "user_id": "primary",
  "financial": {
    "fico_scores": {},
    "nav_credit": {},
    "available_capital": 0,
    "monthly_budget": 0
  },
  "business": {
    "c_corp": {
      "name": "isn.biz?",
      "years_active": 10,
      "industry": "Software/SaaS",
      "naics_codes": []
    },
    "non_profit": {
      "name": "",
      "mission": ""
    }
  },
  "preferences": {
    "automation_minimum": 95,
    "time_available_hours_week": 0,
    "risk_tolerance": "low|medium|high",
    "focus": "set_and_forget"
  },
  "skills": []
}
```

### Step 3: Set Up NAS Backups
```bash
# Create backup destinations
mkdir -p /mnt/baby_nas/opportunity-bot-master/
mkdir -p /mnt/true_nas/opportunity-bot-master/

# Daily backup script
cat > ~/opportunity_backup.sh << 'BACKUP_SCRIPT'
#!/bin/bash
DATE=$(date +%Y%m%d)
tar czf /mnt/baby_nas/opportunity-bot-master/backup_$DATE.tar.gz \
  /mnt/d/workspace/opportunity-research-bot/data/
tar czf /mnt/true_nas/opportunity-bot-master/backup_$DATE.tar.gz \
  /mnt/d/workspace/opportunity-research-bot/data/
# Keep last 30 days
find /mnt/baby_nas/opportunity-bot-master/ -name "backup_*.tar.gz" -mtime +30 -delete
find /mnt/true_nas/opportunity-bot-master/ -name "backup_*.tar.gz" -mtime +30 -delete
BACKUP_SCRIPT

chmod +x ~/opportunity_backup.sh
```

---

## 🤖 DAILY AUTOMATION SETUP

### Cron Job for Daily Scraping
```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily opportunity scraping at 9 AM (1 hour minimum)
0 9 * * * cd /mnt/d/workspace/opportunity-research-bot && venv/bin/python3 production_opportunity_pipeline.py >> logs/daily_$(date +\%Y\%m\%d).log 2>&1

# Daily backup at 11 PM
0 23 * * * /home/jdmal/opportunity_backup.sh

# Weekly deep analysis with Qwen3 (Sunday 2 AM)
0 2 * * 0 cd /mnt/d/workspace/opportunity-research-bot && venv/bin/python3 weekly_analysis.py
```

---

## 📋 WAITING FOR AGENTS

**Currently investigating (parallel):**
1. ⏳ Agent 1: passive_income project deep dive
2. ⏳ Agent 2: Docker container data analysis
3. ⏳ Agent 3: All RAG databases comparison
4. ⏳ Agent 4: C-Corp/GitHub project search

**When complete, we'll know:**
- Exact data in each system
- Where the GB of data went
- What SQLite databases exist
- How to merge everything
- Your company project status

---

## ✅ SUCCESS CHECKLIST

- [ ] Docker rag-chromadb checked (port 8000)
- [ ] All data backed up to timestamped folder
- [ ] Agents complete investigation
- [ ] Consolidation plan finalized
- [ ] User profile created (FICO, Nav, C-Corp data)
- [ ] NAS backups configured
- [ ] Daily automation tested
- [ ] BGE embeddings configured (not mini!)
- [ ] Qwen3 22GB integration verified
- [ ] Never lose data again! 🎉

---

**Next:** Wait for agents to complete, then execute consolidation!
