#!/bin/bash
# Create virtual environment and install dependencies

set -e

echo "=============================================="
echo "🐍 Creating Python Virtual Environment"
echo "=============================================="

# Create venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate and install
echo ""
echo "📦 Installing dependencies..."
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=============================================="
echo "✅ SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "Then run:"
echo "  python production_opportunity_pipeline.py --demo"
echo ""
