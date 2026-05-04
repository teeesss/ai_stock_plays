#!/bin/bash
# ============================================================================
# GIGACPO Social Intelligence Auto-Sync Launcher (V30.4.15)
# Objective: Hardened, venv-aware execution for the X intelligence pipeline.
# ============================================================================

set -euo pipefail

# Define paths
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
REPO_PATH="$DIR"

# 0. Venv Discovery (Matches institutional standard from x.sh/run.sh)
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
LOG="/home/jonesy/x_intel_auto.log"

echo "$(date): Using Venv: $VENV_PYTHON"

# 1. Safety Check: Verify Mount
if [ ! -d "$REPO_PATH" ]; then
    echo "$(date): MOUNT FAILURE" | tee -a "$LOG" >&2
    exit 1
fi

# 2. Run the python script and tee output (captures stdout+stderr)
# Note: x_intel_auto_sync.py now has internal dependency_mgr logic (V30.4.15)
echo "============================================================"
echo "   GIGACPO SOCIAL INTELLIGENCE - AUTO-SYNC STARTED"
echo "============================================================"

"$VENV_PYTHON" -u engine/x_intel_auto_sync.py 2>&1 | tee -a "$LOG"

# 3. Final message
echo "$(date): Social Intelligence Sync Complete" | tee -a "$LOG"
echo "============================================================"
