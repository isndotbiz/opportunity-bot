#!/bin/bash

# Reddit API Configuration Script for Opportunity Bot
# Retrieves credentials from 1Password or prompts for manual entry
# Creates .env file with secure permissions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
SETUP_GUIDE="$SCRIPT_DIR/REDDIT_API_SETUP.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "================================"
    echo "Reddit API Configuration"
    echo "Opportunity Bot Setup"
    echo "================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header
echo ""

# Check if .env already exists
if [ -f "$ENV_FILE" ]; then
    print_warning ".env file already exists at $ENV_FILE"
    read -p "Do you want to reconfigure it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Using existing .env file. Skipping configuration."
        echo ""
        exit 0
    fi
fi

# Check for 1Password CLI
if ! command -v op &> /dev/null; then
    print_error "1Password CLI not found"
    echo ""
    echo "Please install it from:"
    echo "  https://developer.1password.com/docs/cli/get-started/"
    echo ""
    exit 1
fi

print_success "1Password CLI found"
echo ""

# Try to retrieve credentials from 1Password
echo "Step 1: Checking 1Password for Reddit credentials..."
echo ""

REDDIT_ITEM_ID=$(op item list --format=json 2>/dev/null | jq -r '.[] | select(.title == "Reddit API") | .id' 2>/dev/null || true)

if [ -z "$REDDIT_ITEM_ID" ]; then
    print_warning "No 'Reddit API' item found in 1Password"
    echo ""
    echo "You have two options:"
    echo "  1) Enter credentials manually (and optionally save to 1Password)"
    echo "  2) Create a Reddit app first at https://www.reddit.com/prefs/apps"
    echo ""
    read -p "Continue with manual entry? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping Reddit configuration"
        echo ""
        echo "To set up later, run:"
        echo "  $0"
        echo ""
        echo "For detailed instructions, see:"
        echo "  $SETUP_GUIDE"
        exit 0
    fi

    echo ""
    echo "Step 1: Enter Your Reddit API Credentials"
    echo "Get these from: https://www.reddit.com/prefs/apps"
    echo ""
    read -p "Reddit Client ID (personal use script): " CLIENT_ID
    read -sp "Reddit Client Secret: " CLIENT_SECRET
    echo
else
    print_success "Found 'Reddit API' credentials in 1Password"
    echo ""
    echo "Step 1: Retrieving credentials..."

    # Extract credentials from 1Password
    CREDS=$(op item get "$REDDIT_ITEM_ID" --format=json 2>/dev/null)

    # Try to get from standard fields
    CLIENT_ID=$(echo "$CREDS" | jq -r '.fields[] | select(.label == "reddit_client_id") | .value' 2>/dev/null || true)
    CLIENT_SECRET=$(echo "$CREDS" | jq -r '.password' 2>/dev/null || true)

    # Fallback: try to get from custom fields
    if [ -z "$CLIENT_ID" ]; then
        CLIENT_ID=$(echo "$CREDS" | jq -r '.fields[] | select(.label | contains("client_id")) | .value' 2>/dev/null || true)
    fi

    if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
        print_error "Could not retrieve Client ID from 1Password"
        print_info "Please enter manually"
        echo ""
        read -p "Reddit Client ID: " CLIENT_ID
    else
        print_success "Retrieved Client ID from 1Password"
    fi

    if [ -z "$CLIENT_SECRET" ] || [ "$CLIENT_SECRET" = "null" ]; then
        print_error "Could not retrieve Client Secret from 1Password"
        read -sp "Please enter manually - Reddit Client Secret: " CLIENT_SECRET
        echo
    else
        print_success "Retrieved Client Secret from 1Password"
    fi
fi

echo ""

# Validate credentials
if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    print_error "Client ID and Client Secret are required"
    exit 1
fi

# Optional: Save to 1Password
if [ -z "$REDDIT_ITEM_ID" ]; then
    echo "Step 2: Save to 1Password? (optional)"
    read -p "Save credentials to 1Password? (y/n) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating 1Password item..."
        if op item create --category login --title "Reddit API" \
            --vault "Onion" \
            --url "https://reddit.com/prefs/apps" \
            reddit_client_id="$CLIENT_ID" \
            reddit_client_secret="$CLIENT_SECRET" 2>/dev/null; then
            print_success "Saved to 1Password (Onion vault)"
        else
            print_warning "Could not save to 1Password (it may already exist)"
        fi
        echo ""
    fi
fi

# Step 3: Create .env file
echo "Step 2: Creating .env file..."
echo ""

cat > "$ENV_FILE" << EOF
# Reddit API Credentials
# Generated: $(date)
REDDIT_CLIENT_ID=$CLIENT_ID
REDDIT_CLIENT_SECRET=$CLIENT_SECRET
REDDIT_USER_AGENT=OpportunityBot/1.0 (+http://localhost:8080)

# Google Custom Search API (optional)
# Get API key: https://developers.google.com/custom-search/v1/overview
# Get CSE ID: https://cse.google.com/cse/all
GOOGLE_API_KEY=
GOOGLE_CSE_ID=

# Additional APIs (optional)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
EOF

chmod 600 "$ENV_FILE"
print_success ".env file created with secure permissions (600)"
echo ""

# Verify file was created
if [ ! -f "$ENV_FILE" ]; then
    print_error "Failed to create .env file"
    exit 1
fi

# Step 4: Test connection
echo "Step 3: Testing Reddit API connection..."
echo ""

TEST_RESULT=$(python3 << 'PYTHON_TEST' 2>&1 || true)
import os
import sys

# Add the script directory to Python path
sys.path.insert(0, '/mnt/d/workspace/opportunity-research-bot')

try:
    from dotenv import load_dotenv
    load_dotenv('PLACEHOLDER_ENV_FILE')

    import praw

    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        check_for_async=False
    )

    # Test read-only access (no authentication needed)
    test_sub = reddit.subreddit('python')
    test_post = next(test_sub.hot(limit=1))
    print("success")
except ImportError as e:
    if 'praw' in str(e):
        print("praw_not_installed")
    else:
        print(f"import_error:{e}")
except Exception as e:
    print(f"error:{str(e)}")

PYTHON_TEST

# Replace placeholder with actual env file path
TEST_RESULT=$(echo "$TEST_RESULT" | sed "s|PLACEHOLDER_ENV_FILE|$ENV_FILE|g")

# Run actual test
python3 << 'PYTHON_TEST' 2>&1 || true
import os
import sys

# Add the script directory to Python path
sys.path.insert(0, '/mnt/d/workspace/opportunity-research-bot')

try:
    from dotenv import load_dotenv
    load_dotenv('ENV_FILE_PATH')

    import praw

    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        check_for_async=False
    )

    # Test read-only access
    test_sub = reddit.subreddit('python')
    test_post = next(test_sub.hot(limit=1))
    print("✓ Reddit API connection successful!")
    print(f"✓ Tested with subreddit: python")
    print(f"✓ Sample post: {test_post.title[:50]}...")

except ImportError as e:
    if 'praw' in str(e).lower():
        print("⚠ PRAW library not installed")
        print("  Run: pip install -r requirements.txt")
        sys.exit(0)
    else:
        print(f"✗ Import error: {e}")
        sys.exit(1)

except Exception as e:
    error_msg = str(e).lower()
    if 'invalid' in error_msg or 'unauthorized' in error_msg:
        print(f"✗ Invalid credentials: {e}")
        sys.exit(1)
    elif 'timeout' in error_msg or 'connection' in error_msg:
        print(f"⚠ Network error (credentials may be valid): {e}")
        sys.exit(0)
    else:
        print(f"✗ Error: {e}")
        sys.exit(1)

PYTHON_TEST

# Replace placeholder
python3 << PYTHON_TEST 2>&1 || true
import os
import sys

sys.path.insert(0, '/mnt/d/workspace/opportunity-research-bot')

try:
    from dotenv import load_dotenv
    load_dotenv('$ENV_FILE')

    import praw

    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        check_for_async=False
    )

    # Test read-only access
    test_sub = reddit.subreddit('python')
    test_post = next(test_sub.hot(limit=1))
    print("✓ Reddit API connection successful!")
    print(f"✓ Tested with subreddit: python")

except ImportError as e:
    if 'praw' in str(e).lower():
        print("⚠ PRAW library not installed")
        print("  Install with: pip install -r requirements.txt")
        exit(0)
    raise

except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

PYTHON_TEST

echo ""

# Final summary
echo "================================"
print_success "Configuration Complete!"
echo "================================"
echo ""
echo "Your .env file is ready at:"
echo "  $ENV_FILE"
echo ""
echo "Next steps:"
echo "  1. Verify the .env file contains your credentials:"
echo "     cat $ENV_FILE | grep REDDIT"
echo ""
echo "  2. Install dependencies (if not already done):"
echo "     pip install -r $SCRIPT_DIR/requirements.txt"
echo ""
echo "  3. Run the opportunity bot:"
echo "     python3 $SCRIPT_DIR/production_opportunity_pipeline.py"
echo ""
echo "For more information, see:"
echo "  $SETUP_GUIDE"
echo ""
