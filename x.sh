#!/bin/bash
# X Intelligence Auto-Sync Launcher (V30.4.15)
# Objective: Hardened execution environment for the social intelligence pipeline.

# Ensure we are in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "   GIGACPO SOCIAL INTELLIGENCE - AUTO-SYNC BOOTSTRAP"
echo "============================================================"

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "  [FAIL] python3 not found. Please install it."
    exit 1
fi

# Run dependency manager first to resolve any missing modules (like playwright)
echo ">>> Checking Environment..."
python3 engine/dependency_mgr.py

# Execute the sync
echo ">>> Launching Social Intelligence Auto-Sync..."
python3 engine/x_intel_auto_sync.py

echo "============================================================"
echo "   PROCESS COMPLETE"
echo "============================================================"
