# Quickstart Guide (V28.8 Sovereign Intelligence)

## 1. Launching the Command Center
The terminal now operates via a unified Pipeline Orchestration sequence for real-time synchronization. To launch:
1. Initialize the **Web Server Bridge** (server.py) for the API via `start.bat`.
2. Open **`web/semi/index_template.html`** or **`web/ai/index_template.html`** directly in the browser to view the terminals locally.

## 1.5 Sovereign Intelligence Engine (SIE)
To enable high-fidelity email dossiers and web sync:
1. **Dependencies**: `pip install vaderSentiment sumy nltk scikit-learn paramiko`
2. **Authentication**: Add `GMAIL_USER`, `GMAIL_APP_PASS`, `SFTP_HOST`, `SFTP_USER`, and `SFTP_PASS` to your `.env` file.
3. **Dossier Dispatch**: Run `python engine/email_market_synopsis.py` to generate the dossier.
4. **News Intelligence**: Run `./news.sh` (Linux) or `python engine/news_market_synopsis.py --tickers tickers.txt --email` to dispatch the high-density news portal dossier.
5. **Web Sync**: The engines automatically deploy the results to `bmwseals.com/stocks/email` and `bmwseals.com/stocks/news` via `RemoteSync`.

## 2. Automated Synchronization
The terminal is configured for a **"Set and Forget"** production environment:
- **Daily Sync**: Automated market-close update at **4:20 PM EST**.
- **Dossier Dispatch**: Morning (7:30 AM), Evening (4:15 PM), and Overnight (8:01 PM) automated dispatches.

## 3. Adding New Research
1. Add new stocks directly to **`database/CPO_MASTER_DATA.json`**.
2. Update technical deep-dives in **`KNOWLEDGE.md`**.

## 4. Maintenance & Testing
- **Test SIE Email**: Run `python engine/email_market_synopsis.py --test-email --tickers tickers.txt` to verify SMTP and file-based batch loading.
- **Pipeline Rebuild**: Run `python engine/pipeline_orchestrator.py` to rebuild local static bindings.
- **Audit Logs**: Check `logs/` for sector-specific sync status.
- **Full Test Suite**: Run `python run_all_tests.py` to verify logic, layout, and integration.

---
**Troubleshooting**: If the email formatting is off, ensure the `v28_email_styles` CSS block is active in `email_market_synopsis.py`.
