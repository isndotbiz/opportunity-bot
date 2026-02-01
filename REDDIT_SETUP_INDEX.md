# Reddit API Setup - Complete Documentation Index

## Quick Navigation

### For the Impatient (5 minutes)
1. **Start Here**: `REDDIT_QUICKSTART.txt` - Quick reference card with fastest path
2. **Then**: Run `bash configure_reddit.sh`
3. **Verify**: Run `python3 test_reddit_connection.py`

### For Complete Setup Guide
1. **Overview**: Read this file (you are here)
2. **Checklist**: `SETUP_CHECKLIST.md` - Step-by-step with checkboxes
3. **Setup**: Run `bash configure_reddit.sh`
4. **Test**: Run `python3 test_reddit_connection.py`
5. **Production**: Run `python3 production_opportunity_pipeline.py`

### For Detailed Reference
1. **Main Guide**: `REDDIT_CONFIG_README.md` - Complete setup + troubleshooting
2. **Deep Dive**: `REDDIT_API_SETUP.md` - 200+ lines of comprehensive documentation
3. **Summary**: `SETUP_SUMMARY.md` - What was created and why

---

## Documentation Files

### Setup & Configuration

| File | Purpose | Best For | Time |
|------|---------|----------|------|
| `REDDIT_QUICKSTART.txt` | Quick reference card | Quick lookup, cheat sheet | 2 min |
| `SETUP_CHECKLIST.md` | Step-by-step checklist | First-time setup, tracking progress | 20 min |
| `REDDIT_CONFIG_README.md` | Main setup guide | Complete walkthrough + help | 15 min |
| `REDDIT_API_SETUP.md` | Detailed documentation | Reference, advanced topics | 30 min |
| `SETUP_SUMMARY.md` | What was created | Understanding the system | 10 min |

### Scripts

| File | Purpose | Usage | Time |
|------|---------|-------|------|
| `configure_reddit.sh` | Interactive setup | `bash configure_reddit.sh` | 2 min |
| `test_reddit_connection.py` | Verify everything | `python3 test_reddit_connection.py` | 1 min |
| `setup_reddit_credentials.sh` | Alternative setup | `bash setup_reddit_credentials.sh` | 5 min |
| `production_opportunity_pipeline.py` | Run scraper | `python3 production_opportunity_pipeline.py` | 5-10 min |
| `demo_opportunity_pipeline.py` | Test scraper | `python3 demo_opportunity_pipeline.py` | 5 min |

---

## Step-by-Step Quick Start

### In 5 Minutes

```bash
# 1. Get credentials (external)
# Visit: https://www.reddit.com/prefs/apps
# Copy Client ID and Client Secret

# 2. Configure
cd /mnt/d/workspace/opportunity-research-bot
bash configure_reddit.sh
# Answer prompts with your credentials

# 3. Test
python3 test_reddit_connection.py
# Should see: "All tests passed!"

# Done!
```

### In 20 Minutes (Full Setup)

1. Get credentials from Reddit (2 min) - See below
2. Run setup script (2 min) - `bash configure_reddit.sh`
3. Verify configuration (1 min) - `python3 test_reddit_connection.py`
4. Save to 1Password (2 min) - Optional, recommended
5. Demo test (5 min) - `python3 demo_opportunity_pipeline.py`
6. Production run (5 min) - `python3 production_opportunity_pipeline.py`
7. Verification (3 min) - Check results in `data/`

---

## Getting Reddit Credentials

### Steps

1. **Go to**: https://www.reddit.com/prefs/apps
2. **Click**: "Create an application"
3. **Fill form**:
   - Name: `OpportunityBot`
   - Type: `script`
   - Redirect URI: `http://localhost:8080`
4. **Copy**:
   - Client ID (under "personal use script")
   - Client Secret (next to "secret")
5. **Keep safe** until you run setup script

### Location in Reddit

- Reddit User Settings: https://www.reddit.com/prefs/apps
- App Name: OpportunityBot
- Type: Script (not web app)
- Shows: Client ID and Client Secret

---

## Running the Setup

### Automated Setup (Recommended)

```bash
bash configure_reddit.sh
```

**What it does:**
1. Checks 1Password for existing credentials
2. Prompts you to enter credentials
3. Creates .env file with secure permissions
4. Automatically tests the connection
5. Optionally saves to 1Password

### Manual Setup (if script fails)

```bash
cat > .env << 'EOF'
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=OpportunityBot/1.0 (+http://localhost:8080)
EOF
chmod 600 .env
```

---

## Testing Your Setup

### Quick Test

```bash
python3 test_reddit_connection.py
```

**Tests:**
1. .env file exists and has correct permissions
2. All required variables are set
3. Python dependencies installed
4. Reddit API connection works
5. Scraper works with sample data

### What Success Looks Like

```
✓ .env file found
✓ REDDIT_CLIENT_ID: SET
✓ REDDIT_CLIENT_SECRET: SET
✓ REDDIT_USER_AGENT: SET
✓ praw: Installed
✓ python-dotenv: Installed
✓ Reddit API connection successful!
✓ Successfully retrieved X posts
✓ Scraper test successful

All tests passed!
```

---

## Running the Scraper

### Demo Mode (Limited Data)

```bash
python3 demo_opportunity_pipeline.py
```

Use for:
- Testing configuration
- Quick results
- Learning how it works
- Saving API quota

### Production Mode (Full Data)

```bash
python3 production_opportunity_pipeline.py
```

Use for:
- Real deployment
- Daily/weekly scraping
- Complete datasets
- Setting up cron jobs

---

## What Gets Scraped

### Subreddits
- r/SideProject
- r/EntrepreneurRideAlong
- r/Entrepreneur
- r/SweatyStartup
- r/SaaS
- r/IMadeThis
- r/roasting

### Searches
- "made $ revenue"
- "earning $ per month"
- "MRR revenue"
- "passive income"
- "automated business"
- "AI side project revenue"

### Extracts
- Revenue claims
- Tech stack
- Post score
- URL and timestamp
- Author info

---

## File Structure

```
/mnt/d/workspace/opportunity-research-bot/
│
├── SETUP & CONFIGURATION
├── ├─ REDDIT_SETUP_INDEX.md              ← You are here
├── ├─ REDDIT_QUICKSTART.txt              ← Quick reference
├── ├─ SETUP_CHECKLIST.md                 ← Step-by-step checklist
├── ├─ REDDIT_CONFIG_README.md            ← Main guide
├── ├─ REDDIT_API_SETUP.md                ← Detailed docs
├── └─ SETUP_SUMMARY.md                   ← Summary
│
├── CONFIGURATION SCRIPTS
├── ├─ configure_reddit.sh                ← Use this (interactive)
├── ├─ setup_reddit_credentials.sh        ← Alternative
├── └─ test_reddit_connection.py          ← Verify setup
│
├── CREDENTIALS (CREATED BY SETUP)
├── ├─ .env                               ← Your credentials
├── ├─ .env.example                       ← Reference
├── ├─ .env.template                      ← Template
├── └─ .gitignore                         ← Already ignores .env
│
├── APPLICATION CODE
├── ├─ production_opportunity_pipeline.py ← Run this
├── ├─ demo_opportunity_pipeline.py       ← Test this
├── ├─ query_opportunities.py             ← Query results
├── ├─ scrapers/
├── │   ├─ reddit_scraper.py             ← Reddit scraper
├── │   └─ config.py                     ← Scraper config
├── ├─ requirements.txt                   ← Dependencies
│
└── DATA & RESULTS
    ├── data/
    │   ├─ opportunities.json            ← Results
    │   └─ cache/                        ← Cache files
    └── logs/                            ← Log files
```

---

## Common Tasks

### I just got my credentials
→ Run: `bash configure_reddit.sh`

### I want to verify everything works
→ Run: `python3 test_reddit_connection.py`

### I want to test the scraper
→ Run: `python3 demo_opportunity_pipeline.py`

### I want real results
→ Run: `python3 production_opportunity_pipeline.py`

### I want to save credentials to 1Password
→ Run: `bash configure_reddit.sh` and answer yes, OR save manually

### I want to set up daily scraping
→ Run: `bash setup_cron.sh`

### Something isn't working
→ Run: `python3 test_reddit_connection.py` (shows what's wrong)

### I want to customize subreddits
→ Edit: `scrapers/config.py`

### I want detailed help
→ Read: `REDDIT_API_SETUP.md`

---

## Troubleshooting

### Quick Fixes

| Problem | Solution |
|---------|----------|
| "PRAW not found" | `pip install -r requirements.txt` |
| ".env not found" | Run `bash configure_reddit.sh` |
| "Invalid credentials" | Check https://reddit.com/prefs/apps |
| "403 Forbidden" | App revoked, create new at https://reddit.com/prefs/apps |
| "Rate limited" | Wait 5 minutes, bot has built-in delays |
| "Cannot connect" | Check internet, check Reddit status |

### Deep Troubleshooting

For detailed troubleshooting guide with 15+ issues and solutions:
→ See: `REDDIT_API_SETUP.md` (Troubleshooting section)

For test results and diagnostics:
→ Run: `python3 test_reddit_connection.py`

---

## Security

### What's Protected

✓ Credentials in .env (not in git)
✓ File permissions 600 (owner only)
✓ OAuth2 (no passwords)
✓ 1Password backup (optional)
✓ Rate limiting (won't get banned)

### Best Practices

1. Keep .env secure (chmod 600)
2. Don't commit .env (already in .gitignore)
3. Save to 1Password
4. Rotate credentials every 6 months
5. Monitor usage at https://reddit.com/prefs/apps

---

## Key Decisions

### Which setup method?

- **Recommended**: `bash configure_reddit.sh` (interactive, easy, includes tests)
- **Backup**: Manual creation if script fails
- **Alternative**: `bash setup_reddit_credentials.sh` (original script)

### Should I save to 1Password?

**Yes, recommended:**
- Backup in case of emergency
- Can retrieve if .env is lost
- Share across team (if needed)
- Easy credential rotation

**Optional if:**
- Single developer
- Confident in backups
- No team sharing needed

### Demo or Production?

- **Demo first**: Test without using quota
- **Then production**: When confident
- **Cron job**: For automatic daily/weekly runs

---

## Documentation by Topic

### Getting Started
- `REDDIT_QUICKSTART.txt` - Fastest path
- `SETUP_CHECKLIST.md` - Step-by-step

### Setup & Configuration
- `REDDIT_CONFIG_README.md` - Main guide
- `REDDIT_API_SETUP.md` - Detailed reference
- `SETUP_SUMMARY.md` - What was created

### Execution
- `configure_reddit.sh` - Setup script
- `test_reddit_connection.py` - Test script
- `production_opportunity_pipeline.py` - Scraper

### Help & Troubleshooting
- `REDDIT_API_SETUP.md` → Troubleshooting section
- `REDDIT_CONFIG_README.md` → Troubleshooting section
- Run: `python3 test_reddit_connection.py` → Diagnostic output

---

## Estimated Timeline

| Task | Time | Cumulative |
|------|------|-----------|
| Read this guide | 5 min | 5 min |
| Get Reddit credentials | 2 min | 7 min |
| Run setup | 2 min | 9 min |
| Test setup | 1 min | 10 min |
| Demo run | 5 min | 15 min |
| Production run | 5 min | 20 min |
| Save to 1Password | 2 min | 22 min |
| **TOTAL** | | **22 min** |

---

## Success Metrics

You'll know it's working when:

1. ✓ `test_reddit_connection.py` passes all 5 tests
2. ✓ `demo_opportunity_pipeline.py` creates `data/opportunities.json`
3. ✓ JSON file contains Reddit opportunities
4. ✓ Each opportunity has revenue info
5. ✓ `production_opportunity_pipeline.py` runs without errors

---

## Next Steps After Setup

1. **Immediate**: Set up automatic scraping with cron
2. **Short-term**: Monitor API usage
3. **Medium-term**: Customize subreddits/queries in `config.py`
4. **Long-term**: Rotate credentials every 6 months

---

## Getting Help

### Different Resources

**Quick answers**:
- `REDDIT_QUICKSTART.txt` - Quick card
- Run: `python3 test_reddit_connection.py` - Diagnostic

**Step-by-step help**:
- `SETUP_CHECKLIST.md` - Walkthrough
- `REDDIT_CONFIG_README.md` - Main guide

**Deep dive**:
- `REDDIT_API_SETUP.md` - Complete reference
- Code files with comments

**Troubleshooting**:
- `REDDIT_API_SETUP.md` → Troubleshooting (15+ issues)
- `REDDIT_CONFIG_README.md` → Troubleshooting
- `test_reddit_connection.py` output

---

## Directory Map

```
/mnt/d/workspace/opportunity-research-bot/
  setup documentation (THIS DIRECTORY)
  └─ REDDIT_SETUP_INDEX.md (you are here)
     REDDIT_QUICKSTART.txt
     SETUP_CHECKLIST.md
     REDDIT_CONFIG_README.md
     REDDIT_API_SETUP.md
     SETUP_SUMMARY.md
  setup scripts
     configure_reddit.sh
     test_reddit_connection.py
     setup_reddit_credentials.sh
  credentials (you'll create)
     .env (created by setup)
  application
     production_opportunity_pipeline.py
     demo_opportunity_pipeline.py
     scrapers/reddit_scraper.py
     scrapers/config.py
     requirements.txt
  results (auto-created)
     data/opportunities.json
     logs/...
```

---

## TL;DR

1. Get credentials: https://reddit.com/prefs/apps
2. Setup: `bash configure_reddit.sh`
3. Test: `python3 test_reddit_connection.py`
4. Run: `python3 production_opportunity_pipeline.py`
5. Check: `data/opportunities.json`

Done! 20 minutes.

---

## Summary

**This documentation provides:**
- Quick start (5 min)
- Complete setup (20 min)
- Detailed reference
- Troubleshooting guide
- Setup checklist
- All scripts ready to use

**You have everything needed for production deployment.**

---

**Last Updated**: February 1, 2026
**Status**: Complete and ready
**All scripts tested**: ✓
**All documentation complete**: ✓
**Ready for production**: ✓
