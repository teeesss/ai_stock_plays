# Quickstart Guide (V6.1 Autonomous Terminal)

## 1. Launching the Command Center
The terminal now operates via a Web Server Bridge for real-time synchronization. To launch:
1. Double-click **`start.bat`**.
2. Select **Option 2 (Full Intelligence Refresh & Bridge Start)**.

This will:
- Initialize the **Web Server Bridge** (server.py).
- Refresh real-time market data across the 117-ticker universe.
- Open **`cpo_plays.html`** via the local server.

## 2. Automated Synchronization
The terminal is configured for a **"Set and Forget"** production environment:
- **Daily Sync**: Automated market-close update at **4:20 PM EST**.
- **Stealth Extraction**: Uses Ghost-Mode (Playwright) to bypass anti-bot protections.

## 3. Adding New Research
1. Add new stocks to **`cpo_master_ultimate.csv`**.
2. Update technical deep-dives in **`KNOWLEDGE.md`**.
3. Run `start.bat` Option 4 to force-refresh market cap and price data.

## 4. Maintenance & Testing
- **Audit Logs**: Check `logs/server.txt` for autonomous sync status.
- **Handoff**: Run `generate_handoff.bat` to prepare context for Gemini/Claude.
- **Verification**: Run `python tests/verify_stealth.py` to confirm Ghost-Mode integrity.

---
**Troubleshooting**: If the dashboard table appears empty, check `logs/server.txt` for JSON syntax errors or database locks.
