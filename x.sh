#!/bin/bash
set -euo pipefail

# Define paths
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
REPO_PATH="$DIR"

# 0. Venv Discovery
VENV_PATH="./venv"
# Check if current venv is FUNCTIONAL (catches broken mount symlinks)
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
echo "$(date): Using Venv: $VENV_PYTHON"
LOG="/home/jonesy/x_intel.log"

# 1. Safety Check: Verify Mount
if [ ! -d "$REPO_PATH" ]; then
    echo "$(date): MOUNT FAILURE" | tee -a "$LOG" >&2
    exit 1
fi

# 1.5. Ensure dependencies are current (Stealth Mode)
if [ -f "requirements.txt" ]; then
    "$VENV_PYTHON" -m pip install --no-input --no-warn-script-location -r requirements.txt --quiet

    # V28.2: Ensure Playwright Chromium is present
    if grep -q "playwright" requirements.txt; then
        if ! "$VENV_PYTHON" -m playwright install chromium --dry-run &>/dev/null; then
            echo "$(date): Initializing Playwright Chromium..."
            "$VENV_PYTHON" -m playwright install chromium &>/dev/null
        fi
    fi
fi

# 2. Run the python script and tee output (captures stdout+stderr)
# This appends to $LOG and prints to the terminal
"$VENV_PYTHON" -u engine/x_intel_instant_sync.py 2>&1 | tee -a "$LOG"

# 3. Final message (show and log)
echo "$(date): SIE Pulse Dispatched" | tee -a "$LOG"
