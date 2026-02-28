#!/bin/bash

# Reddit API Credentials Setup Script for Opportunity Bot
# This script helps configure Reddit API credentials from 1Password or manual entry

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

echo "================================"
echo "Opportunity Bot - Reddit Setup"
echo "================================"
echo ""

# Check if .env file already exists
if [ -f "$ENV_FILE" ]; then
    echo "Warning: .env file already exists at $ENV_FILE"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Using existing .env file."
        exit 0
    fi
fi

# Check for 1Password CLI
if ! command -v op &> /dev/null; then
    echo "1Password CLI not found. Please install it first:"
    echo "  https://developer.1password.com/docs/cli/get-started/"
    exit 1
fi

echo "Step 1: Checking 1Password for Reddit credentials..."
echo ""

# Try to get Reddit item from 1Password
REDDIT_ITEM=$(op item list --format=json 2>/dev/null | grep -i '"title".*reddit' || true)

if [ -z "$REDDIT_ITEM" ]; then
    echo "No Reddit credentials found in 1Password."
    echo ""
    echo "To set up Reddit API credentials:"
    echo "1. Go to https://www.reddit.com/prefs/apps"
    echo "2. Create a new 'script' application"
    echo "3. You'll get a Client ID and Client Secret"
    echo ""
    read -p "Do you want to (1) enter credentials manually or (2) skip setup? (1/2) " choice

    if [ "$choice" = "1" ]; then
        echo ""
        read -p "Reddit Client ID: " CLIENT_ID
        read -sp "Reddit Client Secret: " CLIENT_SECRET
        echo
        read -p "Reddit Username: " REDDIT_USER
        read -sp "Reddit Password: " REDDIT_PASS
        echo

        echo ""
        echo "Step 2: Save to 1Password? (optional)"
        read -p "Do you want to save these to 1Password? (y/n) " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Creating 1Password item 'Reddit API'..."
            op item create --category login --title "Reddit API" \
                --vault "Onion" \
                --url "https://reddit.com/prefs/apps" \
                reddit_client_id="$CLIENT_ID" \
                reddit_client_secret="$CLIENT_SECRET" \
                reddit_username="$REDDIT_USER" \
                reddit_password="$REDDIT_PASS" 2>/dev/null || \
                echo "Note: Could not save to 1Password automatically. You can add manually."
        fi
    else
        echo "Skipping Reddit credential setup."
        exit 0
    fi
else
    echo "Found Reddit credentials in 1Password!"
    echo "Retrieving credentials..."

    # Parse the item (this is a simplified approach)
    CLIENT_ID=$(op item get "Reddit API" --fields label=reddit_client_id --format=json 2>/dev/null | jq -r '.value' || echo "")
    CLIENT_SECRET=$(op item get "Reddit API" --fields label=reddit_client_secret --format=json 2>/dev/null | jq -r '.value' || echo "")
    REDDIT_USER=$(op item get "Reddit API" --fields label=reddit_username --format=json 2>/dev/null | jq -r '.value' || echo "")
    REDDIT_PASS=$(op item get "Reddit API" --fields label=reddit_password --format=json 2>/dev/null | jq -r '.value' || echo "")
fi

# Step 3: Create .env file
echo ""
echo "Step 3: Creating .env file..."

cat > "$ENV_FILE" << EOF
# Reddit API Credentials
REDDIT_CLIENT_ID=$CLIENT_ID
REDDIT_CLIENT_SECRET=$CLIENT_SECRET
REDDIT_USERNAME=$REDDIT_USER
REDDIT_PASSWORD=$REDDIT_PASS
REDDIT_USER_AGENT=OpportunityBot/1.0 (+http://localhost:8080)

# Google Custom Search API
# Get API key: https://developers.google.com/custom-search/v1/overview
# Get CSE ID: https://cse.google.com/cse/all
GOOGLE_API_KEY=
GOOGLE_CSE_ID=

# Optional: Additional APIs
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
EOF

chmod 600 "$ENV_FILE"
echo ".env file created successfully (permissions: 600)"
echo ""

# Step 4: Test Reddit connection
echo "Step 4: Testing Reddit API connection..."
echo ""

python3 << 'PYTHON' 2>/dev/null || {
    echo "Could not test connection (PRAW may not be installed)"
    echo "Run: pip install -r requirements.txt"
    exit 1
}
import os
import sys
sys.path.insert(0, '/home/jdmal/workspace/opportunity-research-bot')

try:
    from dotenv import load_dotenv
    import praw

    load_dotenv('$ENV_FILE')

    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD')
    )

    user = reddit.user.me()
    print(f"✓ Successfully authenticated as: {user.name}")
    print(f"✓ Account age: {user.created_utc} days old")
    print(f"✓ Comment karma: {user.comment_karma}")
    print(f"✓ Link karma: {user.link_karma}")
    print("")
    print("Reddit API is properly configured!")

except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)
PYTHON

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Your .env file is ready at: $ENV_FILE"
echo ""
echo "Next steps:"
echo "1. Verify .env file contains all credentials"
echo "2. Keep .env file secure (never commit to git)"
echo "3. Run your opportunity bot:"
echo "   python3 bot.py"
echo ""
