#!/bin/bash
# Production setup script for Opportunity Research Bot

set -e

echo "=============================================="
echo "🚀 PRODUCTION SETUP: Opportunity Research Bot"
echo "=============================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your API credentials!"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p rag-business/chroma_db
mkdir -p scrapers/cache
mkdir -p logs

# Test imports
echo ""
echo "🧪 Testing imports..."
python3 -c "
import sys
try:
    from scrapers import RedditScraper, IndieHackersScraper, GoogleDorkingScraper
    import chromadb
    import requests
    print('✅ All imports successful!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Check if Qwen is running
echo ""
echo "🔍 Checking if Qwen LLM is running..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Qwen is running on port 8080"
else
    echo "⚠️  Qwen not detected on port 8080"
    echo "   Start it with: cd llama-cpp-docker && docker-compose up -d"
fi

echo ""
echo "=============================================="
echo "✅ SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit .env and add your API credentials:"
echo "   nano .env"
echo ""
echo "2. Test with demo mode (no API keys needed):"
echo "   python3 production_opportunity_pipeline.py --demo"
echo ""
echo "3. Run production scraping:"
echo "   python3 production_opportunity_pipeline.py"
echo ""
echo "4. Set up daily automation (see setup_cron.sh)"
echo ""
echo "=============================================="
