### 🚀 Active Context: V28.8 (Sovereign Intelligence Hardening)
[Status Synchronized - 2026-04-29]

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V28)**:
   - **Extreme Payload Optimization**: HTML payload remains under 102KB. ACHIEVED: 85KB by transitioning to centralized CSS and high-density layouts.
    - **Ticker Layout Mandate**: EVERY ticker row must follow the 3-line protocol: $TICKER+PRICE on line 1, C: PRICE+PCT on line 2 (for ext sessions), and VAL+PE (including forward '26/'27 estimates) on line 3. Headers are centered.
    - **Valuation Logic**: Terminology standardized to `MCap:`. P/E hierarchy favors forward estimates (`'26 [9.9] '27 [11.4]`) over trailing. Outliers strictly capped at `[-500, 1000]`.
    - **Branding & Accessibility**: Authoritative institutional header includes a live Web Link (`bmwseals.com/stocks/email`) using the `bg_accent` design token.
   - **Hierarchy Leader Mandate**: `engine/market_session.py` is the absolute authority for session/temporal logic. `engine/error_monitor.py` is the authority for exit-point diagnostics.
   - **Identity 146**: Standardize all scraper/rescue identities on Chrome 146.0.7000 (2026-grade).
   - **Import Hardening**: Use recursive try/except blocks in all `engine/` modules to support both root-level discovery and direct execution.
   - **Weekend Freshness**: Lookback window expands to **60h** during Sat/Sun stasis.
   - **Double-Enrichment Fix**: Aggregator returns plain text; flair injected ONLY once in the email script.
   - **Case-Insensitive Badges**: All `source_space_map` lookups are case-normalized.
   - **Ticker Blacklist**: 'FORM' is strictly blacklisted to prevent common-word collisions.
   - **Institutional Source Hardening**: strictly blacklist low-signal sources (e.g., "The Motley Fool").
   - **Article Rotation Engine**: Deployed `sent_news_history.json` ledger to track previously sent URLs for 24h.
   - **Web Synopsis Endpoint**: Automatically deploys the generated email synopsis to `bmwseals.com/email` via `RemoteSync.sync_file()` for instant web access.
   - **Data-Driven Session Detection**: ALWAYS match session badges (AH, OVN, PRE) to the actual data source, not clock time.
   - **24h Ghost Ticker Purge**: Database entries older than 24h must be purged during every save cycle.
   - **Multi-Tier Rescue**: Use a 5-gateway pool (`vx_rescue_fetcher.py`) with OpenGraph HTML scraping fallback.
   - **Unified Error Monitoring**: `engine/error_monitor.py` is integrated into ALL core hierarchy scripts via `atexit`, ensuring a comprehensive error summary is printed at the end of every run for easy diagnostics.

2. **Dependency Guardian (V28)**:
   - **Auto-Restart Protocol**: Uses `os.execv` to automatically refresh the Python process after resolving missing dependencies.

3. **AI UI Generation (V28)**:
   - AI/index.html is a GENERATED artifact. Source of truth is `AI/index_template.html`.

4. **Stealth Session Path Hardening (V28)**:
   - ALWAYS ensure parent directories exist before Playwright `storage_state` calls.
   - Use absolute paths for `stealth_session.json` to prevent CWD-dependent `FileNotFoundError`.

### 🏛️ File Roles
- `engine/email_market_synopsis.py`: SIE Orchestrator. Managed high-density "Cockpit" UI and minified HTML dispatch.
- `engine/macro_aggregator.py`: Multi-source tech-centric news aggregator with weighted scoring.
- `engine/dependency_mgr.py`: Cross-platform dependency resolver with auto-restart (`os.execv`) logic.
- `engine/local_nlp.py`: Statistical NLP hub (LSA, VADER, TF-IDF).
- `engine/yahoo_auth.py`: Centralized stealth session/crumb manager.
- `engine/live_prices.py`: High-stealth price extractor (10-ticker chunks).

### ⚠️ Known Quirks
- Gmail will clip messages if the minification fails or if CSS classes exceed length limits.
- `os.execv` behaves differently on Windows than Linux/Unix (replaces process image).
