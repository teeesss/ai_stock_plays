#!/bin/bash

# RetireFire CPO Intelligence: WSL Sync Script
# To automate this via cron:
# 1. crontab -e
# 2. Add: 0 * * * * /bin/bash /mnt/z/COS_Stock_Plays/research/wsl_sync.sh >> /mnt/z/COS_Stock_Plays/wsl_sync.log 2>&1

# Path to your project on the mapped drive
PROJECT_DIR="/mnt/z/COS_Stock_Plays"

echo "--------------------------------------------------"
echo "⚡ RETIREFIRE: WSL INTELLIGENCE REFRESH [$(date)]"
echo "--------------------------------------------------"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Project directory $PROJECT_DIR not found. Is the Z: drive mapped?"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. Audit Financial Data (yfinance)
python3 research/financial_auditor.py

# 2. Sync Dashboards
python3 research/sync_data.py

# 3. Regenerate LLM Brain
python3 research/sync_brain.py

# 4. Refresh Infographic
python3 research/generate_infographic.py

echo "DONE: Intelligence Refresh Complete."
