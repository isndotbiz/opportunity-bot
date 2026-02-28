#!/bin/bash
# Run Opportunity Bot for Credit Score & Business Credit Opportunities

echo "========================================================================"
echo "Opportunity Bot - Credit Score & Business Credit Focus"
echo "========================================================================"
echo ""

cd /d/workspace/opportunity-research-bot

# Activate venv
source venv/bin/activate 2>/dev/null || {
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

echo "✓ Environment ready"
echo ""

# Start LLM server if not running
echo "Checking LLM server..."
curl -s http://localhost:8080/health > /dev/null 2>&1 || {
    echo "Starting Qwen 30B LLM server..."
    cd /d/workspace/llama-cpp-docker
    docker-compose up -d
    cd /d/workspace/opportunity-research-bot
    echo "Waiting for LLM to start..."
    sleep 30
}

echo "✓ LLM server ready"
echo ""

# Run bot with credit score focus
echo "Running opportunity discovery for:"
echo "  - Credit score improvement opportunities"
echo "  - Equifax business credit building"
echo "  - Credit repair services"
echo "  - Business credit opportunities"
echo ""

python3 production_opportunity_pipeline.py \
    --keywords "credit score improvement,business credit,Equifax business,credit building,700+ FICO,credit repair" \
    --sources reddit,google \
    --max-opportunities 50

echo ""
echo "========================================================================"
echo "✓ COMPLETE! Opportunities saved to ChromaDB"
echo "========================================================================"
echo ""
echo "Query opportunities:"
echo "  python3 query_opportunities.py 'credit score improvement'"
echo "  python3 query_opportunities.py 'Equifax business credit'"
echo ""
