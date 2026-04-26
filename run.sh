#!/bin/bash
# ============================================================================
# GIGACPO Linux Auto-Bootstrapper (V27)
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
    echo "[*] Attempting to install via apt..."
    sudo apt update && sudo apt install python3-venv python3-full -y
fi

# 2. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[*] Virtual environment not found. Creating ./venv..."
    python3 -m venv venv
    echo "[+] Virtual environment created."
fi

# 3. Activate Virtual Environment
echo "[*] Activating virtual environment..."
source venv/bin/activate

# 4. Synchronize Dependencies
echo "[*] Synchronizing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Playwright Hardening
echo "[*] Validating Playwright System Dependencies..."
python -m playwright install --with-deps chromium

# 6. Execute Intelligence Engine
echo "============================================================"
echo " STARTING ENGINE (V27)"
echo "============================================================"
python engine/email_market_synopsis.py
