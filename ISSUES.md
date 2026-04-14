# Active Issues & Resolutions

- **[FIXED] BeautifulSoup/Playwright Missing Dependencies**: Scrapers failed on fresh Windows nodes.
  - **Resolution**: Created global `requirements.txt` and integrated `python -m playwright install chromium`.
- **[FIXED] Windows I/O Unicode Crash**: `ValueError: I/O operation on closed file` during translation.
  - **Resolution**: Implemented `io.TextIOWrapper` with error handling in `translate_intel.py`.
- **[FIXED] Ticker Fragmentation**: Mirror HTML caused $N V D A$ instead of $NVDA.
  - **Resolution**: Deployed V11.0 Surgical Regex with boundary detection.
- **[FIXED] Browser CORS Security Block**: Browser prohibits `fetch()` from local filesystem.
  - **Resolution**: Implemented JS Data Bridge (`research/sync_data.py`).
- **[OPEN] Data Gaps**: Revenue estimates for Tier-2 suppliers (AXTI, Sumitomo) are estimates.
  - **Status**: Research ongoing in `TASKS.md`.
