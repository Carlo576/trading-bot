#!/bin/bash

# Navigate to project root
cd /Users/carlo/trading-bot

# Activate virtual environment
source venv/bin/activate

# Run the live bot (NEW PATH)
python live_bot/email_monitor.py >> bot_log.txt 2>&1

# Add timestamp
echo "--- Run completed at $(date) ---" >> bot_log.txt
