#!/bin/bash
# GIGACPO Social Intelligence Sync Launcher (V30.4.15)
# Objective: Fast, lightweight sync of X intelligence with automated dependency resolution.

set -e

# Ensure we are in the project root
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 0. Venv Discovery (Matches institutional standard)
VENV_PATH="./venv"
if ! "$VENV_PATH/bin/python" --version &>/dev/null; then
    if "$HOME/.venv_gigacpo/bin/python" --version &>/dev/null; then
        VENV_PATH="$HOME/.venv_gigacpo"
    elif [ -f "/home/jonesy/full-stack/market_update/venv/bin/activate" ]; then
        VENV_PATH="/home/jonesy/full-stack/market_update/venv"
    else
        echo "$(date): [!] No functional Python venv found. Reverting to system python3."
        VENV_PYTHON="python3"
    fi
fi

if [ -z "$VENV_PYTHON" ]; then
    VENV_PYTHON="$VENV_PATH/bin/python"
fi

echo "============================================================"
echo "   GIGACPO SOCIAL INTELLIGENCE - AUTO-SYNC BOOTSTRAP"
echo "============================================================"

# Execute the sync (it handles its own dependency checks now)
echo ">>> Launching Social Intelligence Auto-Sync..."
"$VENV_PYTHON" -u engine/x_intel_auto_sync.py

echo "============================================================"
echo "   PROCESS COMPLETE"
echo "============================================================"
