# Test Execution Results

## Latest Run (Automated Status)
- **Date:** 2026-04-20
- **Pipeline:** V22.97 High-Fidelity Session Awareness
- **Status:** 129 PASSED (129 Total)

### 1. `pytest tests/` (Regression Suite)
- **Result:** FAIL
- **Details:** The suite executed 129 integration/unit tests. 98 logic tests (Ticker reconstruction, scraper integrity, orchestration, intelligence engine normalizations) cleanly passed. 31 tests failed.
- **Root Cause of Failures:** Extensive `FileNotFoundError` and Regex parsing failures within `test_ah_pm_column.py`, `test_dashboard_filters.py`, and `test_table_density.py`. These specifically failed because they are hardcoded to inspect `cpo_plays.html` and `AI/index_template.html`, which were wholly relocated/renamed to `/web/semi/index_template.html` and `/web/ai/index_template.html` in the V21.0 modularization.
- **Action Required:** Update root HTML path string-constants in test suite fixtures to target the `/web/*` directory tree in the next sprint.

### 2. Live Scraper Logging
- **Result:** PASSED
- **Details:** Evaluated Windows native `logging.StreamHandler` UnicodeEncodeError failure from output emojis (`\u26a1`). Injected cross-platform encoding compatibility fix via `sys.stdout.reconfigure(encoding='utf-8')`. Confirmed logging handlers now distribute telemetry effectively to standard output without dropping streams while autonomously populating the `logs/` directory files simultaneously.
