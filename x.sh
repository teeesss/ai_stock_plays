#!/bin/bash
# ============================================================================
# GIGACPO Unified Social Intelligence & Dashboard Sync (V30.4.16)
# Targets: @KawzInvests, @PhotonCap, @aleabitoreddit
# Components: Scrape -> Master Rebuild -> OCR -> Live Prices -> Build -> Deploy
# Usage: ./x.sh [--auto|--fast]
# ============================================================================

set -euo pipefail

# Define paths
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
REPO_PATH="$DIR"

# 0. Venv Discovery
VENV_PATH="./venv"
if ! "$VENV_PATH/bin/python" --version &>/dev/null; then
    if "$HOME/.venv_gigacpo/bin/python" --version &>/dev/null; then
        VENV_PATH="$HOME/.venv_gigacpo"
    elif [ -f "/home/jonesy/full-stack/market_update/venv/bin/activate" ]; then
        VENV_PATH="/home/jonesy/full-stack/market_update/venv"
    else
        echo "$(date): FATAL: No functional Python venv found. Please run run.sh first."
        exit 1
    fi
fi
VENV_PYTHON="$VENV_PATH/bin/python"
LOG="/home/jonesy/x_intel.log"

# 1. Safety Check: Verify Mount
if [ ! -d "$REPO_PATH" ]; then
    echo "$(date): MOUNT FAILURE" | tee -a "$LOG" >&2
    exit 1
fi

# 1.5. Ensure dependencies are current (Stealth Mode)
if [ -f "requirements.txt" ]; then
    "$VENV_PYTHON" -m pip install --no-input --no-warn-script-location -r requirements.txt --quiet
    if grep -q "playwright" requirements.txt; then
        if ! "$VENV_PYTHON" -m playwright install chromium --dry-run &>/dev/null; then
            echo "$(date): Initializing Playwright Chromium..."
            "$VENV_PYTHON" -m playwright install chromium &>/dev/null
        fi
    fi
fi

# 2. Parse Arguments
SYNC_MODE=""
if [[ $# -gt 0 ]]; then
    if [[ "$1" == "--auto" || "$1" == "--fast" ]]; then
        SYNC_MODE="--fast"
        echo "$(date): Unified Sync Mode: FAST (3-day lookback)"
    fi
fi

# 3. Execute Unified Intelligence Pipeline
echo "============================================================"
echo " GIGACPO UNIFIED SOCIAL INTELLIGENCE & DASHBOARD REFRESH"
echo "============================================================"
"$VENV_PYTHON" -u engine/x_intel_instant_sync.py $SYNC_MODE 2>&1 | tee -a "$LOG"

# 4. Final message
echo "$(date): Dashboard Sync Complete" | tee -a "$LOG"
echo "============================================================"
