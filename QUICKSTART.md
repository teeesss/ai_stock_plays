# Quickstart Guide

## 1. Launching the Dashboard
The easiest way to view the supply chain terminal is to double-click:
`start.bat`

This will automatically:
- Sync your latest `cpo_master_ultimate.csv` changes.
- Open `cpo_plays.html` in your default browser.

## 2. Adding New Stocks
1. Open `cpo_master_ultimate.csv` in Excel or VS Code.
2. Add a new row.
3. Run `start.bat` to see it reflected in the dashboard.

## 3. Intelligence Refresh (Automation)
To audit real-time financials and generate research bundles for other LLMs:
1. Run `start.bat`.
2. Select **Option 2 (Full Intelligence Refresh)**.
3. This will update prices, P/S ratios, and generate:
   - `database/CPO_BRAIN.json`
   - `infographs/cpo_supply_chain.png`

## 4. Documentation & Research
- All technical research is kept in: `KNOWLEDGE.md`
- Automation setup for WSL/Linux: `AUTOMATION_GUIDE.md`

## 5. Running Tests
If you modify the dashboard code:
```powershell
# Run from root
npm test
```
