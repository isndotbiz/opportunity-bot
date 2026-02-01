#!/bin/bash
# Setup script for FICO-based personalization

echo "=========================================================================="
echo "Setting up FICO-Based Personalization for Opportunity Bot"
echo "=========================================================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo -e "${BLUE}Step 1: Checking Python environment...${NC}"
if [ -d "venv" ]; then
    echo "  ✓ Virtual environment found"
    source venv/bin/activate
else
    echo "  Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

echo ""
echo -e "${BLUE}Step 2: Installing dependencies...${NC}"
pip install -q chromadb requests dataclasses-json

echo ""
echo -e "${BLUE}Step 3: Creating directory structure...${NC}"
mkdir -p credit_integration/profiles
mkdir -p data/chroma_db
echo "  ✓ Directories created"

echo ""
echo -e "${BLUE}Step 4: Generating credit profiles...${NC}"
echo "  Generating ISNBIZ profile..."
python3 credit_integration/fico_parser.py > /dev/null 2>&1

echo "  ✓ Credit profiles generated in credit_integration/profiles/"

echo ""
echo -e "${BLUE}Step 5: Verifying setup...${NC}"

# Check if profiles exist
if [ -f "credit_integration/profiles/isnbiz_profile.json" ]; then
    echo "  ✓ ISNBIZ profile: credit_integration/profiles/isnbiz_profile.json"
else
    echo -e "  ${RED}✗ ISNBIZ profile not found${NC}"
fi

# Check if ChromaDB directory exists
if [ -d "data/chroma_db" ]; then
    echo "  ✓ ChromaDB directory: data/chroma_db"
else
    echo -e "  ${RED}✗ ChromaDB directory not found${NC}"
fi

echo ""
echo "=========================================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================================================="

echo ""
echo "Next Steps:"
echo ""
echo "1. Populate database with opportunities:"
echo "   python3 demo_opportunity_pipeline.py"
echo ""
echo "2. Run personalized search:"
echo "   python3 query_personalized.py 'AI automation opportunities'"
echo ""
echo "3. Interactive mode:"
echo "   python3 personalized_opportunity_bot.py"
echo ""
echo "4. Get portfolio advice:"
echo "   python3 personalized_opportunity_bot.py isnbiz"
echo "   (then type 'advice' in interactive mode)"
echo ""
echo "5. Compare business entities:"
echo "   python3 query_personalized.py 'passive income' isnbiz"
echo "   python3 query_personalized.py 'passive income' hroc"
echo ""
echo "=========================================================================="
echo ""
echo "Credit Profiles Available:"
echo "  • isnbiz - ISNBIZ, Inc (C-Corp)"
echo "  • hroc   - HROC (Non-Profit)"
echo ""
echo "Features Enabled:"
echo "  ✓ FICO credit score integration"
echo "  ✓ Nav business credit data"
echo "  ✓ Risk-based opportunity matching"
echo "  ✓ Investment capacity filtering"
echo "  ✓ Business type-specific recommendations"
echo "  ✓ Personalized portfolio strategy"
echo ""
echo "=========================================================================="
