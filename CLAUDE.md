### 🚀 Active Context: V30.6.10 (Cross-Channel Pricing Parity)
[Status Synchronized - 2026-05-05]

### 🚀 Current Milestone: V30.6.10 - Cross-Channel Pricing Parity [2026-05-05]
- **Single Source of Truth**: `ticker_utils.py` is the SOLE authority for `is_legit_ticker`, `get_ticker_session_data`, and `render_valuation_row`. NEVER duplicate these in individual engines.
- **Preposition Flair Fix**: `TICKER_BLACKLIST` now includes common English words (ON, AT, BY, IF, IN, TO...) to prevent false price flair.
- **News/Email Cross-Channel Parity**: Both `/news` and `/email` portals now use the exact same pricing and session logic. Zero divergence.
- **Close Price Fidelity**: News watchlist now shows `CLOSE: $X.XX ±X.X%` anchored to `get_authoritative_prev_close`.
- **Numerical High-to-Low Sorting**: News watchlist sorted by `pct` descending — consistent with email dashboard.
- **Ticker Cockpit (V30.6.9 legacy)**: Engine decoupled into `engine/ticker_dashboard.py`. Columns: PRICE | AH/OVN/PRE/L | % CHG | CLOSE | C % | MCAP | '26 P/E | '27 P/E.

## 🚀 Version: V30.4.19 (Unified Narrative & Anchor Fidelity)
Status: **PRODUCTION DEPLOYED — VERIFIED ✅ 2026-05-05**

📊 **Project Status: Sovereign Intel**
- **Current Tier**: V30.6.10 (Cross-Channel Pricing Parity)
- **Critical Progress**: News and email pipelines fully unified. ticker_utils.py is single source of truth.
- **Next Milestone**: V30.7 — Automated sector-specific weighting for narrative generation.

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V30.2)**:
   - **Extreme Payload Optimization**: HTML payload remains under 102KB. ACHIEVED: 85KB by transitioning to centralized CSS and high-density layouts.
    - **Narrative Hardening (V30.2)**: RSS summaries are aggressively stripped of HTML before synthesis to prevent split-URL corruption. THEME_BLACKLIST expanded to include NBSP, SESSION PERFORMANCE, IPC, and DISCLOSURE fragments.
    - **Period-Stripping Mandate**: All narrative catalysts MUST have internal periods replaced with spaces and trailing periods stripped to prevent Gmail from misinterpreting text as clickable links.
    - **Ticker Layout Mandate**: EVERY ticker row must follow the 3-line protocol: $TICKER+PRICE on line 1, C: PRICE+PCT on line 2 (for ext sessions), and VAL+PE (including forward '26/'27 estimates) on line 3. Headers are centered.
    - **Valuation Logic**: Terminology standardized to `MCap:`. P/E hierarchy favors forward estimates (`'26 [9.9] '27 [11.4]`) over trailing. Outliers strictly capped at `[-500, 1000]`.
    - **Branding & Accessibility**: Authoritative institutional header includes a live Web Link (`bmwseals.com/stocks/email`) using the **Sovereign Blue (#38bdf8)** design token. Injected "🕰️ ARCHIVE" buttons into both email and web cockpit headers for historical access.
   - **Archival Intelligence Engine**: Deployed `SynopsisArchiveManager` to maintain a 48-hour rolling history (`synopsis_history.json`) of market dossiers, integrated into the master dispatch pipeline.
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
    - **Session-Aware Narrative Pipeline**: Dossier includes real-time market context scraped from StockMarketWatch (PRE), CNBC (MID), and Edward Jones (POST). **Hardened with signature-based extraction, case-insensitive junk rejection, and editorial keyword gates.**
    - **Anti-Fragile Intelligence Stack (V28.8.10)**: Uses `database/ai_intel_cache.json` as a primary fallback for AI summaries. Each intelligence card MUST display its source-level timestamp (e.g., `[ CNBC @ 12:41 EST ]`).
    - **Session-Based Gating (V28.8.10)**: Edward Jones (EDJ) summaries are strictly gated to After-Hours (AH) and CLOSED sessions to prevent post-market noise during live trading.
    - **Archive Synchronization (V28.8.10)**: Every dossier saved to the archive must immediately trigger `RemoteSync.sync_file()` for both the individual HTML file and the archive index.
   - **Data-Driven Session Detection**: ALWAYS match session badges (AH, OVN, PRE) to the actual data source, not clock time.
   - **24h Ghost Ticker Purge**: Database entries older than 24h must be purged during every save cycle.
   - **Multi-Tier Rescue**: Use a 5-gateway pool (`vx_rescue_fetcher.py`) with OpenGraph HTML scraping fallback.
    - **Unified Error Monitoring**: `engine/error_monitor.py` is integrated into ALL core hierarchy scripts via `atexit`, ensuring a comprehensive error summary is printed at the end of every run for easy diagnostics.
    - **Regex Guard Mandate**: ALWAYS use word boundaries (e.g., `r"<p\b"`) when searching for paragraph tags to avoid false-positive matches with `<path>`, `<picture>`, or `<pre>` tags.
    - **News Portal Mirror Mandate (V30.4)**: `engine/news_market_synopsis.py` must maintain 100% aesthetic and logical parity with the main email engine while optimized for high-density web access (e.g., removed company notes from watchlist).
    - **Email Anti-Clip Protocol**: All dossiers MUST include a hidden anti-clip UUID and timestamp in the footer to prevent Gmail from collapsing repeated market updates.
    - **Centralized Ticker Intelligence (V30.4.8)**: `MacroAggregator.fetch_ticker_news` is the authoritative gateway for ticker-specific news, enforcing strict freshness (36h/60h/72h for macro, **168h/7-day for tickers**) and safety gates.
    - **Hierarchical Utility Layer (V30.4.10)**: Shared rendering and extraction logic (EPS, session badges) and **authoritative news categorization and date formatting (format_news_date)** moved to `ticker_utils.py` to decouple engines and centralize institutional standards.
    - **Strict Section Exclusivity (V30.4.9)**: Enforced 100% isolation for technical semiconductor news. Articles identified as semi-trade news are strictly prohibited from the Macro section, regardless of section capacity, to prevent intelligence bleed.
    - **Mobile UI Hardening (V30.4.13)**: Enforced 75px tap-target density for the Back-to-Top (`.home-btn`) component on mobile viewports (<768px). Injected mandatory `viewport` meta tags to ensure responsive media query execution on high-DPI mobile devices.
    - **Mobile UI Refinement (V30.4.14)**: Reduced the mobile Back-to-Top button size by 33% (to 50px) to improve spatial balance while maintaining high-contrast visibility and responsive authority. ✅
     - **Ticker Utils Single-Source Mandate (V30.6.10)**: ticker_utils.py is the ABSOLUTE AUTHORITY for is_legit_ticker, TICKER_BLACKLIST, get_ticker_session_data, and render_valuation_row. ANY engine MUST import, NEVER re-implement locally.
     - **Pre-hydrated PE Priority (V30.6.10)**: render_valuation_row checks p_data.get(pe26) first before recalculating from EPS trend.
     - **Refactor Safety Rule (V30.6.10)**: When removing a block of methods, always audit for collateral removals. grep for helpers after bulk deletions.

2. **Dependency Guardian (V28)**:
   - **Auto-Restart Protocol**: Uses `os.execv` to automatically refresh the Python process after resolving missing dependencies.

3. **AI UI Generation (V28)**:
   - AI/index.html is a GENERATED artifact. Source of truth is `AI/index_template.html`.

4. **Stealth Session Path Hardening (V28)**:
   - ALWAYS ensure parent directories exist before Playwright `storage_state` calls.
   - Use absolute paths for `stealth_session.json` to prevent CWD-dependent `FileNotFoundError`.

### 🏛️ File Roles
- `run.sh`: Sovereign Intelligence Email Orchestrator. Dispatches the high-density "Cockpit" UI.
- `news.sh`: News Intelligence Portal Engine. Optimized for high-density web reporting and news email dispatch.
- `ticker.sh`: Thin launcher → delegates to `engine/ticker_dashboard.py`. Do NOT run directly on NAS drives.
- `x.sh`: Unified Social Intelligence & Dashboard Sync. Handles scraping, OCR, and web portal deployment.
- `engine/ticker_utils.py`: **SINGLE SOURCE OF TRUTH** — ticker legitimacy, session data, valuation rendering.
- `engine/ticker_dashboard.py`: Ticker Cockpit HTML + CLI renderer.
- `engine/email_market_synopsis.py`: SIE Orchestrator logic.
- `engine/news_market_synopsis.py`: News Portal Engine logic.
- `engine/x_intel_instant_sync.py`: Unified Social/Web sync logic (supports `--auto` mode).
- `docs/ARCHITECTURE_V28.md`: V28.8 Definitive Architecture Reference.
- `docs/INTELLIGENCE_MANUAL.md`: Scoring hierarchy and signal governance guide.

### ⚠️ Known Quirks
- Gmail will clip messages if the minification fails or if CSS classes exceed length limits.
- `os.execv` behaves differently on Windows than Linux/Unix (replaces process image).
- **NAS Drive (X:) Rule**: NEVER use `wsl` or `bash` for scripts on X: drive. PowerShell native ONLY.
- **DO NOT open files locally** via VSCode or shell commands from AI — view internally using Antigravity tools.
