# Reddit API Setup Guide for Opportunity Bot

## Overview
The Opportunity Bot uses the Reddit API to scrape business opportunity posts from various subreddits. This guide will help you obtain and configure Reddit API credentials.

## Step 1: Get Reddit API Credentials

### Option A: Create a New Reddit App (Recommended)

1. Go to: https://www.reddit.com/prefs/apps
2. Scroll to the bottom and click "Create an application" or "Create another app"
3. Fill in the form:
   - **Name**: OpportunityBot (or your preferred name)
   - **App Type**: Choose "script"
   - **Description**: "Reddit opportunity scraper for business intelligence"
   - **Redirect URI**: http://localhost:8080 (required but not used for script apps)
4. Click "Create app"
5. You'll see a box with your credentials:
   - **Client ID**: The text under "personal use script"
   - **Client Secret**: The text next to "secret"

### Example Credentials Format
```
Client ID: a1b2c3d4e5f6gh
Client Secret: a1b2c3d4e5f6g_1234567890_abcdefg
User Agent: OpportunityBot/1.0 (+http://localhost:8080)
```

## Step 2: Store Credentials in 1Password

### Create a New Login Item

1. Open 1Password
2. Click "Create Item" and select "Login"
3. Fill in:
   - **Title**: "Reddit API"
   - **Website**: https://reddit.com/prefs/apps
   - **Username**: (leave empty or use your Reddit username)
   - **Password**: Your Client Secret
   - **Add custom field "reddit_client_id"**: Your Client ID
4. Save to the "Onion" vault

### Using 1Password CLI

```bash
op item create --category login --title "Reddit API" \
  --vault "Onion" \
  --url "https://reddit.com/prefs/apps" \
  reddit_client_id="YOUR_CLIENT_ID" \
  reddit_client_secret="YOUR_CLIENT_SECRET"
```

## Step 3: Configure the Bot

### Option A: Interactive Setup (Recommended)

```bash
cd /mnt/d/workspace/opportunity-research-bot
bash setup_reddit_credentials.sh
```

This script will:
1. Check 1Password for existing credentials
2. Help you enter credentials manually if needed
3. Create a secure `.env` file with proper permissions (600)
4. Test the Reddit API connection

### Option B: Manual Setup

1. Create `.env` file in `/mnt/d/workspace/opportunity-research-bot/`:
```bash
cat > /mnt/d/workspace/opportunity-research-bot/.env << 'EOF'
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=OpportunityBot/1.0 (+http://localhost:8080)

# Google Custom Search API (optional)
GOOGLE_API_KEY=
GOOGLE_CSE_ID=

# Other APIs (optional)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
EOF
```

2. Set secure permissions:
```bash
chmod 600 /mnt/d/workspace/opportunity-research-bot/.env
```

## Step 4: Verify Configuration

### Quick Test

```bash
cd /mnt/d/workspace/opportunity-research-bot
python3 -c "
from dotenv import load_dotenv
from scrapers.reddit_scraper import RedditScraper
import os

load_dotenv()
try:
    scraper = RedditScraper()
    print('✓ Reddit API credentials are valid!')
except Exception as e:
    print(f'✗ Error: {e}')
"
```

### Full Test

```bash
cd /mnt/d/workspace/opportunity-research-bot
python3 -c "
from scrapers.reddit_scraper import RedditScraper

scraper = RedditScraper()
print('Testing Reddit API connection...')
# This will test actual API access
opportunities = scraper.scrape_subreddit('SideProject', limit=5)
print(f'✓ Successfully retrieved {len(opportunities)} posts')
"
```

## Troubleshooting

### "Reddit API credentials missing!"
- Check that `.env` file exists in `/mnt/d/workspace/opportunity-research-bot/`
- Verify `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` are set
- Run: `cat .env | grep REDDIT`

### "Invalid credentials"
- Verify credentials are correct at https://www.reddit.com/prefs/apps
- Check for extra whitespace or quotes in `.env`
- Try regenerating the Client Secret in Reddit app settings

### "401 Unauthorized"
- Your app may have been revoked/deleted
- Create a new application at https://www.reddit.com/prefs/apps
- Update the credentials in `.env`

### "403 Forbidden"
- You may be rate-limited
- Check Reddit API usage limits
- Reduce scraping frequency or add delays

## Security Best Practices

1. **Never commit `.env` to git**
   - It's already in `.gitignore`
   - Verify: `git status | grep .env`

2. **Use secure permissions**
   - `chmod 600 .env` (read/write for owner only)

3. **Rotate credentials regularly**
   - Delete old apps at https://www.reddit.com/prefs/apps
   - Create new credentials every 3-6 months

4. **Monitor API usage**
   - Check app details at https://www.reddit.com/prefs/apps
   - Look for unusual activity

## Reddit API Rate Limits

- **Default**: 60 requests per minute
- **Authenticated**: Can make up to 60 requests per minute
- **Bot strategy**: Add delays between requests (1-2 seconds)

The bot includes rate limiting in:
- `RATE_LIMIT_REDDIT = 30` requests per minute (conservative)
- `time.sleep(1)` between subreddit searches
- `time.sleep(2)` between subreddit changes

## Advanced Configuration

### Custom Subreddits

Edit `/mnt/d/workspace/opportunity-research-bot/scrapers/config.py`:
```python
REDDIT_SUBREDDITS = [
    "SideProject",
    "Entrepreneur",
    "SaaS",
    # Add more subreddits here
]
```

### Custom Search Queries

Edit `/mnt/d/workspace/opportunity-research-bot/scrapers/config.py`:
```python
REDDIT_SEARCH_QUERIES = [
    "made $ revenue",
    "earning $ per month",
    # Add more queries here
]
```

## Next Steps

1. Set up credentials using `setup_reddit_credentials.sh`
2. Verify with test commands above
3. Run the full pipeline: `python3 production_opportunity_pipeline.py`
4. Check `/mnt/d/workspace/opportunity-research-bot/data/` for results

## Additional Resources

- [Reddit API Documentation](https://www.reddit.com/dev/api)
- [PRAW (Python Reddit API Wrapper)](https://praw.readthedocs.io/)
- [Create Reddit App](https://www.reddit.com/prefs/apps)
- [1Password CLI Docs](https://developer.1password.com/docs/cli/)
