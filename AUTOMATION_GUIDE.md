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

## 3. Manual Setup (The GUI Way)

1. Open **Task Scheduler**.
2. Click **Create Basic Task**.
3. Name: `CPO_Intelligence_Sync`.
4. Trigger: **Weekly** (e.g., Monday 9 AM).
5. Action: **Start a Program**.
6. Program/Script: `z:\COS_Stock_Plays\start.bat`.
7. Add Arguments: `2` (This tells the batch file to run the Full Refresh).
8. Start in: `z:\COS_Stock_Plays`.

## 4. Other Financial "Skills" (Pip Installs)

To further enhance your scripts, consider installing these via `pip`:

- `pip install alphavantage` (Alternative to yfinance for high-quality fundamental data)
- `pip install nasdaq-datalink` (For institutional-grade macroeconomic datasets)
- `pip install beautifulsoup4` (For building custom scrapers in `research/`)
