# Automation & Scheduling Guide

To keep your CPO Ecosystem Intelligence fresh without manual work, you can set up **Windows Task Scheduler** to run a full refresh every week or every morning.

## 1. The Strategy

We will schedule a "Silent Refresh" that runs Option 2 of your `start.bat` in the background.

## 2. Setup via Command Line (The Fast Way)

Open PowerShell as **Administrator** and run this command to refresh your intelligence every Monday at 9:00 AM:

```powershell
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c z:\COS_Stock_Plays\start.bat 2' -WorkingDirectory 'z:\COS_Stock_Plays'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "XTweetsRefresh" -Description "Syncs CPO data, audits financials, and exports LLM bundles."
```

## 2.5 Sovereign Dossier Scheduling (V26.12)

The Sovereign Intelligence Engine is designed for high-frequency market alignment. It is recommended to schedule dispatches at **Market Pre-Open**, **Market Close**, and **Sunday Night / Overnight**.

**PowerShell Automation:**
```powershell
# Morning Intelligence (7:30 AM) - PRE/Premarket State
# V26.12: Guarantees <5m Price Freshness via JIT refresh.
$a1 = New-ScheduledTaskAction -Execute 'python' -Argument 'engine\email_market_synopsis.py' -WorkingDirectory 'z:\COS_Stock_Plays'
$t1 = New-ScheduledTaskTrigger -Daily -At 7:30am
Register-ScheduledTask -Action $a1 -Trigger $t1 -TaskName "SIE_Morning_Dispatch"

# Evening Intelligence (4:15 PM) - AH/Afterhours State
$a2 = New-ScheduledTaskAction -Execute 'python' -Argument 'engine\email_market_synopsis.py' -WorkingDirectory 'z:\COS_Stock_Plays'
$t2 = New-ScheduledTaskTrigger -Daily -At 4:15pm
Register-ScheduledTask -Action $a2 -Trigger $t2 -TaskName "SIE_Evening_Dispatch"

# Overnight/Sunday Intelligence (8:01 PM) - OVN/Overnight State (BOATS Data)
$a3 = New-ScheduledTaskAction -Execute 'python' -Argument 'engine\email_market_synopsis.py' -WorkingDirectory 'z:\COS_Stock_Plays'
$t3 = New-ScheduledTaskTrigger -Daily -At 8:01pm
Register-ScheduledTask -Action $a3 -Trigger $t3 -TaskName "SIE_Overnight_Dispatch"
```

## 3. Work Log Transparency (V26.12)
When running via Task Scheduler, review your `soe_intel.log` for high-fidelity work status:
- **`[INFO] [CACHE]`**: Confirms if the run is utilizing fresh price/news data.
- **`[INFO] [LIVE]`**: Indicates a just-in-time fetch triggered by stale cache.
- **`[INFO] [ALPHA]`**: Confirms the NLP ranking engine successfully isolated the top headline.

## 3. Manual Setup (The GUI Way)
1. Open **Task Scheduler**.
2. Click **Create Basic Task**.
3. Name: `SIE_Intelligence_Sync`.
4. Action: **Start a Program**.
5. Program/Script: `python.exe`.
6. Add Arguments: `engine\email_market_synopsis.py`.
7. Start in: `z:\COS_Stock_Plays`.

## 4. Automated Environment Hardening (V26.12)

The Sovereign pipeline now includes the **Auto-Dependency Guardian** utilizing `os.execv` to restart seamlessly on dependency resolution.

Simply run the script:
```bash
python engine/email_market_synopsis.py
```
If any libraries (vaderSentiment, sumy, curl_cffi, etc.) are missing, the script will **automatically install them** and inject them seamlessly without failing out of the schedule.

## 5. Hierarchy of Truth: Market Temporal Logic (V26.14)

To prevent code duplication and inconsistent state across scripts (e.g., fetching prices on weekends when we shouldn't), the ecosystem follows a strict **Temporal Hierarchy**:

*   **Leader**: `engine/market_session.py` (`MarketSession` class).
*   **Rules**:
    1.  **NO LOCAL CALCULATIONS**: Individual scripts are strictly forbidden from calculating their own `weekday()` or `hour()` to decide if markets are open.
    2.  **STASIS GATE**: All data-fetch scripts must call `session.is_market_stasis()` before starting a run.
    3.  **WEEKEND STASIS**: Defined as Saturday (all day) and Sunday (until 6 PM EST). During this window, all runs skip network fetches unless the `--force` flag is used.
    4.  **TIMEZONE ANCHOR**: All logic is anchored to **US/Eastern** via the hierarchy leader to ensure consistency across local and cloud environments.

**Integration Example:**
```python
from market_session import MarketSession
session = MarketSession()
if session.is_market_stasis():
    print("[STASIS] Market closed. Run aborted.")
    return
```
