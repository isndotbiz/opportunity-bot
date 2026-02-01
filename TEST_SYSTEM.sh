#!/bin/bash
echo "════════════════════════════════════════════════════════════"
echo "🧪 TESTING PRODUCTION OPPORTUNITY RESEARCH BOT"
echo "════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Test demo pipeline
echo "📊 Running demo pipeline..."
python3 production_opportunity_pipeline.py --demo 2>&1 | tail -20

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ TEST COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🎯 Try queries now:"
echo '  python3 query_opportunities.py "high automation"'
echo '  python3 query_opportunities.py "passive income"'
echo '  python3 query_opportunities.py "under $1000"'
echo ""
