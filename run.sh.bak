#!/bin/bash
# ============================================================================
# GIGACPO Linux Auto-Bootstrapper (V28.3)
# Automatically creates venv, syncs dependencies, and handles Playwright
# ============================================================================

set -e

echo "============================================================"
echo " GIGACPO SOVEREIGN INTELLIGENCE - LINUX STARTUP"
echo "============================================================"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 1. Ensure Python venv capabilities
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 could not be found. Please install python3."
    exit 1
fi

if ! python3 -c "import venv" &> /dev/null; then
    echo "[!] python3-venv is missing."
    read -p "[?] Install python3-venv via apt? (y/n): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        sudo apt update -y &>/dev/null
        sudo apt install python3-venv python3-full -y
    else
        echo "[!] Installation cancelled. Venv creation will likely fail."
    fi
fi

# 2. Determine Venv Path and Create if missing
VENV_PATH="./venv"
# Check if current venv is missing or non-functional (catches broken mount symlinks)
if ! "$VENV_PATH/bin/python" --version &>/dev/null && ! "$HOME/.venv_gigacpo/bin/python" --version &>/dev/null; then
    echo "[*] Virtual environment not found or broken. Attempting to create ./venv..."
    if ! python3 -m venv "$VENV_PATH" 2>/dev/null; then
        echo "[!] FAILED to create venv in current directory (likely a mount issue)."
        VENV_PATH="$HOME/.venv_gigacpo"
        echo "[*] Creating venv in local filesystem: $VENV_PATH"
        mkdir -p "$VENV_PATH"
        python3 -m venv "$VENV_PATH"
    fi
fi

# Final resolution of VENV_PATH
VENV_PYTHON="$VENV_PATH/bin/python"
if ! "$VENV_PYTHON" --version &>/dev/null; then
    if "$HOME/.venv_gigacpo/bin/python" --version &>/dev/null; then
        VENV_PATH="$HOME/.venv_gigacpo"
        VENV_PYTHON="$VENV_PATH/bin/python"
    fi
fi

# 1.5. Ensure dependencies are current (Stealth Mode)
if [ -f "requirements.txt" ]; then
    echo "[*] Checking dependencies..."
    "$VENV_PYTHON" -m pip install --upgrade pip --quiet
    "$VENV_PYTHON" -m pip install --no-input --no-warn-script-location -r requirements.txt --quiet

    # V28.2: Ensure Playwright Chromium is present
    if grep -q "playwright" requirements.txt; then
        echo "[*] Verifying Playwright..."
        if ! "$VENV_PYTHON" -m playwright install chromium --dry-run &>/dev/null; then
            echo "[*] Initializing Playwright Chromium (this may take a moment)..."
            "$VENV_PYTHON" -m playwright install chromium &>/dev/null
        fi
    fi
fi

# 6. Execute Intelligence Engine (Restored Flags & Logging)
SOE_LOG="/home/jonesy/soe_intel.log"
"$VENV_PYTHON" -u engine/email_market_synopsis.py --test-email --tickers tickers.txt 2>&1 | tee -a "$SOE_LOG"

dispatch_ts=$(date "+%a %b %d %I:%M:%S %p %Z %Y")
echo "$dispatch_ts: SIE Pulse Dispatched" | tee -a "$SOE_LOG"
