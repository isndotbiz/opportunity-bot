#!/bin/bash
# Modern Opportunity Bot - Installation Script
# Installs all dependencies and verifies setup

set -e  # Exit on error

echo "========================================================================="
echo "MODERN OPPORTUNITY BOT - INSTALLATION"
echo "========================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python 3.11+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi
echo ""

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel -q
echo -e "${GREEN}✅ pip upgraded${NC}"
echo ""

# Install dependencies
echo "Installing modern dependencies..."
echo "This may take a few minutes..."
pip install -r requirements_modern.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers..."
echo "This will download ~300MB of browser binaries..."
playwright install chromium

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Playwright browsers installed${NC}"
else
    echo -e "${YELLOW}⚠️  Playwright installation failed${NC}"
    echo "You may need to install system dependencies:"
    echo "  sudo apt-get install libglib2.0-0 libnss3 libnspr4 libdbus-1-3"
fi
echo ""

# Install Playwright system dependencies (on Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing Playwright system dependencies..."
    playwright install-deps chromium 2>/dev/null || echo -e "${YELLOW}⚠️  May need sudo for system dependencies${NC}"
    echo ""
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.template .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and add your Reddit API credentials${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi
echo ""

# Create data directory
echo "Creating data directory..."
mkdir -p data/chroma_db
echo -e "${GREEN}✅ Data directory created${NC}"
echo ""

# Run tests
echo "========================================================================="
echo "RUNNING SETUP TESTS"
echo "========================================================================="
echo ""

python test_modern_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================================================="
    echo -e "${GREEN}✅ INSTALLATION COMPLETE!${NC}"
    echo "========================================================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure API credentials:"
    echo "   Edit .env and add your Reddit API credentials"
    echo "   Get them from: https://www.reddit.com/prefs/apps"
    echo ""
    echo "2. Run the modern pipeline:"
    echo "   source venv/bin/activate"
    echo "   python modern_opportunity_pipeline.py"
    echo ""
    echo "3. Or test individual scrapers:"
    echo "   python scrapers/reddit_scraper_modern.py"
    echo "   python scrapers/indiehackers_scraper_modern.py"
    echo ""
    echo "Documentation:"
    echo "   - Quick start: README_MODERN.md"
    echo "   - Full guide: MODERN_UPGRADE_GUIDE.md"
    echo ""
else
    echo ""
    echo "========================================================================="
    echo -e "${RED}❌ INSTALLATION INCOMPLETE${NC}"
    echo "========================================================================="
    echo ""
    echo "Some tests failed. Please check the output above."
    echo ""
    echo "Common issues:"
    echo "1. Playwright not installed properly"
    echo "   Solution: playwright install chromium"
    echo ""
    echo "2. Missing system dependencies"
    echo "   Solution: sudo apt-get install libglib2.0-0 libnss3 libnspr4"
    echo ""
    echo "3. Python version < 3.11"
    echo "   Solution: Install Python 3.11+"
    echo ""
    exit 1
fi
