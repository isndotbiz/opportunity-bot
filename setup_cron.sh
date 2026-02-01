#!/bin/bash
# Setup automated daily scraping with cron

set -e

WORKSPACE="/mnt/d/workspace/opportunity-research-bot"
SCRIPT="$WORKSPACE/production_opportunity_pipeline.py"
LOG_DIR="$WORKSPACE/logs"
CRON_TIME="0 9 * * *"  # Run daily at 9 AM

echo "=============================================="
echo "⏰ CRON JOB SETUP: Daily Opportunity Scraping"
echo "=============================================="

# Create logs directory
mkdir -p "$LOG_DIR"

# Create wrapper script for cron
CRON_SCRIPT="$WORKSPACE/run_daily_scraping.sh"

cat > "$CRON_SCRIPT" << 'EOF'
#!/bin/bash
# Daily opportunity scraping wrapper script

# Set working directory
cd /mnt/d/workspace/opportunity-research-bot

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run pipeline with logging
DATE=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="logs/scraping_$DATE.log"

echo "Starting opportunity scraping at $(date)" >> "$LOG_FILE"

python3 production_opportunity_pipeline.py >> "$LOG_FILE" 2>&1

echo "Completed at $(date)" >> "$LOG_FILE"

# Keep only last 30 days of logs
find logs/ -name "scraping_*.log" -mtime +30 -delete
EOF

chmod +x "$CRON_SCRIPT"

echo "✅ Created cron wrapper script: $CRON_SCRIPT"
echo ""

# Display cron entry
echo "📋 Add this to your crontab:"
echo ""
echo "# Daily opportunity scraping at 9 AM"
echo "$CRON_TIME $CRON_SCRIPT"
echo ""

# Ask if user wants to auto-install
read -p "Install cron job automatically? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup current crontab
    crontab -l > /tmp/crontab.bak 2>/dev/null || true

    # Check if entry already exists
    if crontab -l 2>/dev/null | grep -q "$CRON_SCRIPT"; then
        echo "⚠️  Cron job already exists, skipping..."
    else
        # Add new cron entry
        (crontab -l 2>/dev/null || true; echo ""; echo "# Daily opportunity scraping"; echo "$CRON_TIME $CRON_SCRIPT") | crontab -
        echo "✅ Cron job installed!"
    fi

    # Show current crontab
    echo ""
    echo "📋 Current crontab:"
    crontab -l
else
    echo "⏭️  Skipped auto-install"
    echo "   Run manually: crontab -e"
    echo "   Then add: $CRON_TIME $CRON_SCRIPT"
fi

echo ""
echo "=============================================="
echo "✅ CRON SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "🔧 Cron Management Commands:"
echo "   • View crontab:   crontab -l"
echo "   • Edit crontab:   crontab -e"
echo "   • Remove crontab: crontab -r"
echo ""
echo "📊 Monitor Logs:"
echo "   • Latest log:     tail -f logs/scraping_*.log"
echo "   • All logs:       ls -lh logs/"
echo ""
echo "🧪 Test Run:"
echo "   • Manual test:    $CRON_SCRIPT"
echo ""
echo "=============================================="
