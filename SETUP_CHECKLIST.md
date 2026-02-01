# Reddit API Setup Checklist for Opportunity Bot

**Project**: Opportunity Research Bot
**Task**: Configure Reddit API credentials for production scraping
**Target**: 20 minutes to full configuration

---

## Pre-Setup (5 minutes)

- [ ] Read this checklist (2 minutes)
- [ ] Review `REDDIT_QUICKSTART.txt` (2 minutes)
- [ ] Ensure internet connection (1 minute)

---

## Step 1: Get Reddit API Credentials (2 minutes)

- [ ] Go to: https://www.reddit.com/prefs/apps
- [ ] Click "Create an application" or "Create another app"
- [ ] Fill in form:
  - [ ] Name: `OpportunityBot`
  - [ ] App Type: `script`
  - [ ] Description: `Reddit opportunity scraper for business intelligence`
  - [ ] Redirect URI: `http://localhost:8080`
- [ ] Click "Create app"
- [ ] Copy **Client ID** (text under "personal use script")
- [ ] Copy **Client Secret** (text next to "secret")
- [ ] Store credentials temporarily for next step

**Credentials Ready**: ✓

---

## Step 2: Run Interactive Setup (2 minutes)

Choose ONE of these options:

### Option A: Interactive Setup (Recommended)

```bash
cd /mnt/d/workspace/opportunity-research-bot
bash configure_reddit.sh
```

- [ ] Script starts
- [ ] Script checks 1Password (or says not found)
- [ ] Enter Client ID when prompted
- [ ] Enter Client Secret when prompted
- [ ] Save to 1Password? (y/n) - Choose based on preference
- [ ] Script creates .env file
- [ ] Script tests Reddit connection automatically
- [ ] See "✓ Reddit API connection successful!" message

**Stop here and verify with Step 3 before continuing**

### Option B: Manual Setup

If script doesn't work:

```bash
cd /mnt/d/workspace/opportunity-research-bot
cat > .env << 'EOF'
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=OpportunityBot/1.0 (+http://localhost:8080)
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
EOF

chmod 600 .env
```

- [ ] .env file created
- [ ] .env file has 600 permissions: `ls -l .env`
- [ ] Credentials in file: `cat .env | grep REDDIT`

**Proceed to Step 3**

---

## Step 3: Verify Configuration (1 minute)

Run comprehensive test:

```bash
python3 test_reddit_connection.py
```

You should see:

- [ ] ✓ .env file found
- [ ] ✓ REDDIT_CLIENT_ID: SET
- [ ] ✓ REDDIT_CLIENT_SECRET: SET
- [ ] ✓ REDDIT_USER_AGENT: SET
- [ ] ✓ praw: Installed
- [ ] ✓ python-dotenv: Installed
- [ ] ✓ Reddit API connection successful
- [ ] ✓ Successfully retrieved posts from r/python
- [ ] ✓ Sample opportunity shown
- [ ] ✓ Scraper test successful

**All tests passed: ✓**

If any test fails:
- [ ] Check troubleshooting in `REDDIT_API_SETUP.md`
- [ ] Run `cat .env` to verify credentials
- [ ] Check file permissions: `ls -l .env`
- [ ] Check internet connection: `ping reddit.com`

---

## Step 4: Optional - Backup to 1Password

If you didn't save during setup:

### Via 1Password GUI

- [ ] Open 1Password
- [ ] Click "Create Item"
- [ ] Select "Login"
- [ ] Fill in:
  - [ ] Title: `Reddit API`
  - [ ] Website: `https://reddit.com/prefs/apps`
  - [ ] Custom field: `reddit_client_id` = your Client ID
  - [ ] Password: your Client Secret
- [ ] Save to: `Onion` vault
- [ ] Verify you can retrieve it

### Via 1Password CLI

```bash
op item create --category login \
  --title "Reddit API" \
  --vault "Onion" \
  --url "https://reddit.com/prefs/apps" \
  reddit_client_id="YOUR_CLIENT_ID" \
  reddit_client_secret="YOUR_CLIENT_SECRET"
```

- [ ] Command executes successfully
- [ ] See item created message
- [ ] Verify: `op item get "Reddit API"`

**This step is optional but recommended for security**

---

## Step 5: Run Demo Test (5 minutes)

Test with demo mode to verify everything:

```bash
python3 demo_opportunity_pipeline.py
```

- [ ] Script starts without errors
- [ ] See "REDDIT SCRAPING:" section
- [ ] Script accesses multiple subreddits
- [ ] Script finds opportunities
- [ ] Script completes without errors
- [ ] See summary of opportunities found

Check results:

```bash
ls -la data/
cat data/opportunities.json | head -50
```

- [ ] `data/` directory exists
- [ ] `opportunities.json` file created
- [ ] JSON contains Reddit opportunities

---

## Step 6: Production Run (5-10 minutes)

Run full production scraper:

```bash
python3 production_opportunity_pipeline.py
```

- [ ] Script starts without errors
- [ ] Scrapes all subreddits
- [ ] Shows progress for each subreddit
- [ ] Script completes successfully
- [ ] See final opportunity count

Check production results:

```bash
cat data/opportunities.json | python3 -m json.tool | head -100
```

- [ ] Results are properly formatted JSON
- [ ] Contains multiple opportunities
- [ ] Each has title, revenue, URL, timestamp
- [ ] Data looks reasonable

---

## Step 7: Post-Setup Verification

### File Security Check

```bash
# Check .env is secure
ls -l .env
# Should show: -rw------- (600)

# Check it's gitignored
cat .gitignore | grep env
# Should show: .env
```

- [ ] .env has 600 permissions
- [ ] .env is in .gitignore
- [ ] No .env in git status

### Credential Rotation Plan

- [ ] Document when credentials were created: `Feb 1, 2026`
- [ ] Plan rotation date: ~3-6 months from now
- [ ] Set reminder to regenerate credentials
- [ ] Save new credentials to 1Password when updated

### Data Location

```bash
# Check data location
ls -la data/
```

- [ ] `data/` directory exists
- [ ] Contains `opportunities.json`
- [ ] Contains timestamp file for last run

---

## Step 8: (Optional) Set Up Automated Scraping

For production environment:

```bash
bash setup_cron.sh
```

- [ ] Script guides through cron setup
- [ ] Choose frequency (daily/weekly)
- [ ] Cron job created
- [ ] Verify: `crontab -l | grep opportunity`

---

## Troubleshooting Checklist

### "PRAW not found"
- [ ] Install: `pip install -r requirements.txt`
- [ ] Verify: `python3 -c "import praw; print(praw.__version__)"`

### "Cannot find .env"
- [ ] File exists: `ls -l .env`
- [ ] In correct location: `pwd` should be `/mnt/d/workspace/opportunity-research-bot`
- [ ] Create with: `bash configure_reddit.sh`

### "Invalid credentials"
- [ ] Check values: `cat .env | grep REDDIT`
- [ ] No extra spaces or quotes
- [ ] Credentials match https://www.reddit.com/prefs/apps
- [ ] Try regenerating Secret in app settings

### "403 Forbidden"
- [ ] App may be revoked: https://www.reddit.com/prefs/apps
- [ ] Create new app if needed
- [ ] Update credentials in .env

### "Cannot connect to Reddit"
- [ ] Check internet: `ping reddit.com`
- [ ] Check Reddit status: https://www.redditstatus.com/
- [ ] Try again in 5 minutes

### "Rate limited (429)"
- [ ] This is normal if running frequently
- [ ] Bot has built-in delays
- [ ] Wait 5 minutes before running again

### Test suite shows failures

Run individual tests:

```bash
# Test .env file
test -f .env && echo "✓ .env exists" || echo "✗ .env missing"

# Test credentials
cat .env | grep REDDIT_CLIENT_ID

# Test Python import
python3 -c "import praw; print('✓ PRAW works')"

# Test Reddit connection
python3 test_reddit_connection.py
```

---

## Success Criteria

✓ **Setup is complete when you have:**

- [ ] .env file in `/mnt/d/workspace/opportunity-research-bot/.env`
- [ ] Credentials set in .env (not empty)
- [ ] File permissions are 600
- [ ] `test_reddit_connection.py` passes all 5 tests
- [ ] Demo script runs without errors
- [ ] Production script creates `data/opportunities.json`
- [ ] JSON contains Reddit opportunities with revenue info
- [ ] Credentials backed up in 1Password (optional but recommended)

✓ **You can now:**

- [ ] Run `python3 production_opportunity_pipeline.py` anytime
- [ ] Get fresh opportunities from Reddit weekly/daily
- [ ] Integrate results with other data sources
- [ ] Deploy to production environment

---

## Quick Reference Commands

### Most Important

```bash
# Interactive setup (5-10 minutes total)
bash configure_reddit.sh

# Verify everything works
python3 test_reddit_connection.py

# Run the scraper
python3 production_opportunity_pipeline.py
```

### Utilities

```bash
# Check .env exists
ls -l .env

# Check credentials are set
cat .env | grep REDDIT

# View results
cat data/opportunities.json | python3 -m json.tool

# Test PRAW directly
python3 -c "import praw; reddit = praw.Reddit(client_id='test', client_secret='test', user_agent='test'); print('✓ PRAW works')"
```

### Troubleshooting

```bash
# Install dependencies
pip install -r requirements.txt

# Regenerate .env
bash configure_reddit.sh

# Full test
python3 test_reddit_connection.py

# Check 1Password
op item list | grep -i reddit
```

---

## Time Estimate

| Step | Time | Optional? |
|------|------|-----------|
| Get Reddit credentials | 2 min | Required |
| Run setup script | 2 min | Required |
| Verify with tests | 1 min | Required |
| Backup to 1Password | 2 min | Optional |
| Demo run | 5 min | Optional but recommended |
| Production run | 5-10 min | Required once |
| Automation setup | 3 min | Optional |
| **TOTAL** | **~20 min** | |

---

## Final Notes

### Security Reminders

- ✓ .env is gitignored (credentials won't leak)
- ✓ Using OAuth2 (no passwords stored)
- ✓ File permissions 600 (only owner can read)
- ✓ 1Password backup (in case of emergency)
- ✓ Rate limiting enabled (won't get banned)

### Next Steps After Setup

1. **Daily**: Monitor API usage at https://www.reddit.com/prefs/apps
2. **Weekly**: Run production scraper or set up cron
3. **Monthly**: Check for new opportunities
4. **Quarterly**: Rotate credentials
5. **As Needed**: Update subreddits or search queries in `config.py`

### Need Help?

1. Read: `REDDIT_API_SETUP.md` (detailed guide)
2. Read: `REDDIT_CONFIG_README.md` (complete reference)
3. Check: `REDDIT_QUICKSTART.txt` (quick card)
4. Run: `python3 test_reddit_connection.py` (diagnostics)
5. Review: `scrapers/config.py` (customization)

---

## Sign-Off

- [ ] All steps completed
- [ ] All checks passed
- [ ] Ready for production
- [ ] Credentials secured
- [ ] Automation planned (optional)

**Status: READY FOR PRODUCTION** ✓

**Last Updated**: February 1, 2026
**Estimated Completion**: February 1, 2026 + 20 minutes
