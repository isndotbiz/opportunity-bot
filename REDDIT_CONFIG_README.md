# Reddit API Configuration for Opportunity Bot

## Status

This document provides step-by-step instructions to configure Reddit API credentials for the Opportunity Bot. All tools and templates are already in place.

## Quick Start (5 Minutes)

### 1. Get Reddit API Credentials

Go to **https://www.reddit.com/prefs/apps** and create a new application:

1. Click "Create an application" or "Create another app"
2. Fill in the form:
   - **Name**: OpportunityBot
   - **App type**: Choose "script"
   - **Description**: Reddit opportunity scraper for business intelligence
   - **Redirect URI**: http://localhost:8080 (required, not used)
3. Click "Create app"
4. Copy your credentials:
   - **Client ID** - the text under "personal use script"
   - **Client Secret** - the text next to "secret"

### 2. Configure the Bot

Run the interactive configuration script:

```bash
cd /mnt/d/workspace/opportunity-research-bot
bash configure_reddit.sh
```

This script will:
- Check 1Password for existing Reddit credentials
- Prompt you to enter credentials manually if needed
- Create a secure `.env` file with proper permissions (600)
- Test the API connection automatically

### 3. Verify Configuration

Test that everything is working:

```bash
python3 test_reddit_connection.py
```

This will:
- Check the .env file exists
- Verify all required variables are set
- Test the Reddit API connection
- Test the scraper with a sample subreddit
- Show detailed results for each step

### 4. Run the Bot

Once configuration is verified:

```bash
python3 production_opportunity_pipeline.py
```

Results will be saved to `/mnt/d/workspace/opportunity-research-bot/data/`

---

## Files Provided

### Configuration Files

| File | Purpose | Usage |
|------|---------|-------|
| `.env.example` | Template with placeholder values | Reference |
| `.env.template` | Template for Reddit + Google APIs | Copy and edit |
| `.env` | Your actual credentials | Created by setup script |

### Setup Scripts

| File | Purpose | Usage |
|------|---------|-------|
| `configure_reddit.sh` | Interactive setup (recommended) | `bash configure_reddit.sh` |
| `setup_reddit_credentials.sh` | Original setup script | Backup alternative |
| `test_reddit_connection.py` | Comprehensive test suite | `python3 test_reddit_connection.py` |

### Documentation

| File | Purpose |
|------|---------|
| `REDDIT_API_SETUP.md` | Detailed setup guide with troubleshooting |
| `REDDIT_QUICKSTART.txt` | Quick reference card |
| `REDDIT_CONFIG_README.md` | This file |

### Scrapers

| File | Purpose |
|------|---------|
| `scrapers/reddit_scraper.py` | Main Reddit scraper (uses PRAW) |
| `scrapers/config.py` | Configuration for scraping (queries, subreddits, etc.) |

---

## Manual Setup (If Scripts Don't Work)

### Create .env File

```bash
cat > /mnt/d/workspace/opportunity-research-bot/.env << 'EOF'
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_from_reddit
REDDIT_CLIENT_SECRET=your_client_secret_from_reddit
REDDIT_USER_AGENT=OpportunityBot/1.0 (+http://localhost:8080)

# Google Custom Search (optional)
GOOGLE_API_KEY=
GOOGLE_CSE_ID=

# Other APIs (optional)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
EOF
```

### Secure the File

```bash
chmod 600 /mnt/d/workspace/opportunity-research-bot/.env
```

### Verify Permissions

```bash
ls -l /mnt/d/workspace/opportunity-research-bot/.env
# Should show: -rw------- (600 permissions)
```

---

## Using 1Password for Credential Storage

### Option 1: Automatic (during setup)

When you run `configure_reddit.sh`, it will ask if you want to save credentials to 1Password.

### Option 2: Manual via 1Password GUI

1. Open 1Password
2. Create a new Login item with:
   - **Title**: Reddit API
   - **Website**: https://reddit.com/prefs/apps
   - **Username**: (optional, your Reddit username)
   - **Password**: Your Client Secret
   - **Custom field "reddit_client_id"**: Your Client ID
3. Save to the "Onion" vault

### Option 3: Using 1Password CLI

```bash
op item create --category login \
  --title "Reddit API" \
  --vault "Onion" \
  --url "https://reddit.com/prefs/apps" \
  reddit_client_id="YOUR_CLIENT_ID" \
  reddit_client_secret="YOUR_CLIENT_SECRET"
```

Then retrieve with:

```bash
op item get "Reddit API" --fields label=reddit_client_id
op item get "Reddit API" --fields label=reddit_client_secret
```

---

## Testing Your Configuration

### Quick Test

```bash
cd /mnt/d/workspace/opportunity-research-bot

# Test that .env is readable
cat .env | grep REDDIT

# Test credentials work
python3 << 'EOF'
import os
from dotenv import load_dotenv
import praw

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
    check_for_async=False
)

# Test with a single post
post = next(reddit.subreddit("python").hot(limit=1))
print(f"✓ Success! Got post: {post.title[:50]}...")
EOF
```

### Full Test Suite

```bash
python3 test_reddit_connection.py
```

This runs 5 tests:
1. Checks .env file exists and has correct permissions
2. Verifies all required environment variables are set
3. Checks Python dependencies (PRAW, python-dotenv)
4. Tests actual Reddit API connection
5. Tests the scraper with a sample subreddit

---

## Running the Scraper

### Dry Run (Demo Mode)

```bash
python3 demo_opportunity_pipeline.py
```

This runs the scraper with limited data to test without consuming API quota.

### Full Run (Production)

```bash
python3 production_opportunity_pipeline.py
```

This:
- Scrapes all configured subreddits
- Searches for revenue/business opportunity mentions
- Extracts revenue claims and tech stacks
- Saves results to `/mnt/d/workspace/opportunity-research-bot/data/`

### Custom Scraping

```bash
python3 << 'EOF'
from scrapers.reddit_scraper import RedditScraper

scraper = RedditScraper()

# Scrape specific subreddit
opps = scraper.scrape_subreddit("SideProject", limit=10)
print(f"Found {len(opps)} opportunities")

for opp in opps:
    print(f"  - {opp['title']}")
    print(f"    Revenue: {opp['revenue_claim']}")
    print(f"    URL: {opp['url']}\n")
EOF
```

---

## Troubleshooting

### Error: "Reddit API credentials missing!"

**Cause**: REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET is not set

**Solution**:
1. Check .env file exists: `ls -la /mnt/d/workspace/opportunity-research-bot/.env`
2. Check it's readable: `cat /mnt/d/workspace/opportunity-research-bot/.env | grep REDDIT`
3. Recreate with: `bash configure_reddit.sh`

### Error: "Invalid credentials" or "401 Unauthorized"

**Cause**: Client ID or Secret is incorrect

**Solutions**:
1. Verify credentials at https://www.reddit.com/prefs/apps
2. Check for typos or extra whitespace in .env
3. Check for quotes in .env: `REDDIT_CLIENT_ID="value"` is wrong, should be `REDDIT_CLIENT_ID=value`
4. Create a new app: https://www.reddit.com/prefs/apps
5. Regenerate the Client Secret in app settings

### Error: "PRAW not found" or "ModuleNotFoundError"

**Cause**: Python dependencies not installed

**Solution**:
```bash
pip install -r /mnt/d/workspace/opportunity-research-bot/requirements.txt
```

### Error: "403 Forbidden"

**Cause**: Your Reddit app was revoked or deleted

**Solutions**:
1. Check app status at https://www.reddit.com/prefs/apps
2. Create a new app if needed
3. Update credentials in .env

### Error: "429 Too Many Requests" or rate limiting

**Cause**: Too many API requests in a short time

**Solutions**:
1. Add delays: `time.sleep(2)` between requests
2. Reduce subreddit limit: use `limit=10` instead of `limit=100`
3. Bot already implements rate limiting - wait before running again

### Error: "Cannot connect to Reddit" or timeout

**Cause**: Network issue or Reddit is down

**Solutions**:
1. Check internet connection
2. Try again in a few minutes
3. Check Reddit status: https://www.redditstatus.com/
4. Verify you're not IP-banned (unlikely with normal use)

---

## Reddit API Details

### What Credentials You Need

- **Client ID**: Public identifier for your app
- **Client Secret**: Private key (keep secret!)
- **User Agent**: Required by Reddit API
  - Format: `AppName/Version (+url)`
  - Default: `OpportunityBot/1.0 (+http://localhost:8080)`

### Authentication Method

The bot uses **OAuth2 read-only access**:
- No username/password needed
- Only reads public data
- Safer than full authentication
- Supported by PRAW (Python Reddit API Wrapper)

### Rate Limits

- 60 requests per minute (authenticated or read-only)
- Bot uses 30 requests/minute (conservative)
- Includes delays to stay well under limits

### What Gets Scraped

**Subreddits**:
- r/SideProject
- r/EntrepreneurRideAlong
- r/Entrepreneur
- r/SweatyStartup
- r/SaaS
- r/IMadeThis
- r/roasting

**Search Queries**:
- "made $ revenue"
- "earning $ per month"
- "MRR revenue"
- "passive income"
- "automated business"
- "AI side project revenue"

**Extracted Data**:
- Post title and content
- Revenue claims ($X/month)
- Tech stack mentions
- Score and engagement
- URL and timestamp

---

## Security Best Practices

### Protect Your Credentials

1. **Never commit .env to git**
   - Already in `.gitignore`
   - Verify: `cat /mnt/d/workspace/opportunity-research-bot/.gitignore | grep env`

2. **Use secure file permissions**
   - `chmod 600 .env` (read/write for owner only)
   - Check: `ls -l .env` should show `------` permissions

3. **Store backup in 1Password**
   - Use `configure_reddit.sh` to auto-save
   - Or save manually as described above

4. **Rotate credentials periodically**
   - Delete old apps at https://www.reddit.com/prefs/apps
   - Create new credentials every 3-6 months
   - Update .env with new values

### Monitor API Usage

1. Go to https://www.reddit.com/prefs/apps
2. Click on your app
3. Check "monthly usage" statistics
4. Look for unusual activity

### Secure Deployment

When deploying to production:
1. Don't hardcode credentials in code
2. Use .env files
3. Set environment variables in deployment system
4. Use secure secret management (1Password, AWS Secrets, etc.)
5. Rotate credentials after deployment
6. Monitor API usage

---

## Advanced Configuration

### Customize Subreddits

Edit `/mnt/d/workspace/opportunity-research-bot/scrapers/config.py`:

```python
REDDIT_SUBREDDITS = [
    "SideProject",
    "Entrepreneur",
    "SaaS",
    "YourSubreddit",  # Add your own
]
```

### Customize Search Queries

Edit `/mnt/d/workspace/opportunity-research-bot/scrapers/config.py`:

```python
REDDIT_SEARCH_QUERIES = [
    "made $ revenue",
    "your custom query",
]
```

### Adjust Rate Limiting

Edit `/mnt/d/workspace/opportunity-research-bot/scrapers/config.py`:

```python
RATE_LIMIT_REDDIT = 30  # requests per minute
```

### Change Filter Criteria

Edit `/mnt/d/workspace/opportunity-research-bot/scrapers/config.py`:

```python
MIN_REVENUE_MENTION = 100  # minimum $ amount
MAX_OPPORTUNITIES_PER_SOURCE = 50
```

---

## Next Steps

1. **Get credentials**: Visit https://www.reddit.com/prefs/apps
2. **Run setup**: `bash configure_reddit.sh`
3. **Test**: `python3 test_reddit_connection.py`
4. **Run scraper**: `python3 production_opportunity_pipeline.py`
5. **Check results**: `ls /mnt/d/workspace/opportunity-research-bot/data/`

---

## Additional Resources

- [Reddit API Documentation](https://www.reddit.com/dev/api)
- [PRAW Documentation](https://praw.readthedocs.io/)
- [Create Reddit App](https://www.reddit.com/prefs/apps)
- [1Password CLI Docs](https://developer.1password.com/docs/cli/)
- [OAuth2 Explained](https://oauth.net/2/)

---

## Support

For issues or questions:

1. Check the detailed guide: `REDDIT_API_SETUP.md`
2. Check the quick reference: `REDDIT_QUICKSTART.txt`
3. Run the test suite: `python3 test_reddit_connection.py`
4. Review the scrapers: `scrapers/reddit_scraper.py`

---

Last updated: 2026-02-01
Ready for production deployment.
