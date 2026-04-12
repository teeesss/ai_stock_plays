@echo off
setlocal enabledelayedexpansion

echo ##################################################
echo #   ^⚡ RETIREFIRE: CPO TERMINAL AUTOMATION ^⚡     #
echo ##################################################
echo.

:MENU
echo 1. Launch Terminal (Static - open HTML directly)
echo 2. Launch Web Server Bridge (http://localhost:5174 + auto-sync)
echo 3. Full Intelligence Refresh (Sync + Audit + Bundle + Map)
echo 4. Live Price Refresh Only (fast, ~30 sec)
echo 5. LLM Sync Only (Export JSON/MD for Grok)
echo 6. Exit
echo.
set /p choice="Select Option (1-6): "

if "%choice%"=="1" goto SYNC_OPEN
if "%choice%"=="2" goto WEB_SERVER
if "%choice%"=="3" goto FULL_REFRESH
if "%choice%"=="4" goto PRICES_ONLY
if "%choice%"=="5" goto BUNDLE_ONLY
if "%choice%"=="6" exit
goto MENU

:SYNC_OPEN
echo [1/2] Syncing Local Data Bridge...
python engine/generate_CPO_BRAIN.py
echo [2/2] Opening Dashboard...
start "" "cpo_plays.html"
goto END

:WEB_SERVER
echo =========================================================
echo   GIGACPO Web Server Bridge
echo   Dashboard: http://localhost:5174
echo   Auto-sync: 4:20 PM EST (Mon-Fri) after market close
echo   Manual sync: click SYNC button in the terminal
echo   Stop: Ctrl+C in this window
echo =========================================================
echo.
echo Install deps if needed: pip install fastapi uvicorn apscheduler
echo.
python server.py
goto END

:FULL_REFRESH
echo [1/4] Running Financial Auditor (deep data fetch)...
python engine/financial_auditor.py
echo [2/4] Fetching Live Prices...
python engine/live_prices.py
echo [3/4] Exporting LLM Brain Bundles (JSON + MD)...
python engine/generate_CPO_BRAIN.py
echo [4/4] Launching Terminal...
start "" "cpo_plays.html"
echo.
echo SUCCESS: Ecosystem Fully Synced.
goto END

:PRICES_ONLY
echo Fetching live prices...
python engine/live_prices.py
echo Done. Reload your browser or reopen cpo_plays.html.
goto END

:BUNDLE_ONLY
echo Exporting Intelligence Bundles...
python engine/generate_CPO_BRAIN.py
echo - `database/CPO_BRAIN.json` (Structured Data)
echo - `database/CPO_BRAIN.md` (Technical context)
echo Done. Share with Grok.
goto END

:END
echo.
echo Process Complete.
timeout /t 3
exit
