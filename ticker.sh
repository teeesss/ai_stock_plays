#!/bin/bash
# ============================================================================
# GIGACPO Ticker Intelligence Launcher (V30.6.7)
# ============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Determine Venv Path
VENV_PATH="./venv"
if [ -f "$VENV_PATH/Scripts/python.exe" ]; then
    VENV_PYTHON="$VENV_PATH/Scripts/python.exe"
elif [ -f "$VENV_PATH/bin/python" ]; then
    VENV_PYTHON="$VENV_PATH/bin/python"
else
    VENV_PYTHON="python3"
fi

# Launch the decoupled engine
"$VENV_PYTHON" -u engine/ticker_dashboard.py "$@"
