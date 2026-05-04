## 🛠 V30.4.13 Mobile UI Polish Final (2026-05-04)
- [x] **Mobile Icon Finalization**: Increased "Back-to-Top" button size by 25% (to 75px) on mobile viewports for optimized tap-target fidelity. ✅

## 🛠 V30.4.12 Dual-Ticker Hardening & UI Polish (2026-05-04)
- [x] **Dual-Ticker Labeling Hardened**: Centralized `$SIVE.TO/$SIVEF` labeling in `ticker_utils.py` to ensure institutional-grade representation of Sivers Semiconductors. ✅
- [x] **Pricing Discovery Persistence**: Maintained `SIVE.ST` (Stockholm) as the machine-readable pricing authority while projecting the dual-symbol moniker in all UI outputs. ✅
- [x] **Responsive Navigation Hardening**: Re-engineered the "Back-to-Top" button (`.home-btn`) with a high-contrast black/white aesthetic and increased tap-target density (60px) for mobile devices. ✅
- [x] **Parity Synchronization**: Verified 100% labeling consistency between the News Portal (`news_market_synopsis.py`) and the Email Dossier (`email_market_synopsis.py`). ✅

## 🛠 V30.4.10 News Intelligence Freshness Hardening (2026-05-04)
- [x] **7-Day Freshness Lookback**: Extended ticker-specific news threshold to 168h (7 days) in `macro_aggregator.py` to increase intelligence density. ✅
- [x] **Date Visibility Utility**: Created centralized `format_news_date` in `ticker_utils.py` for standardized article timestamping. ✅
- [x] **Intelligence Transparency**: Injected human-readable publication dates (e.g., "May 04") into all news rows in `news_market_synopsis.py`. ✅
- [x] **Quota Verification**: Confirmed 15-article minimum for ticker intel using multi-day coverage and deep-backfill logic. ✅

## 🛠 V30.4.9 News Portal Hardening & Synchronization (2026-05-04)
- [x] **Institutional Timestamping**: Fixed missing date/time in portal header by injecting centralized logic from `ticker_utils.py`. ✅
- [x] **Ticker-Specific Intel Density**: Implemented a 3-tier aggressive backfill (Pass 1: Surgical RSS, Pass 2: Deep Tracker, Pass 3: Raw News Pool) to guarantee a 15-article minimum. ✅
- [x] **Semiconductor Technical Isolation**: Enforced strict categorization to prevent trade-specific semi news (EE Times/Semi Wiki) from bleeding into the Macro section. ✅
- [x] **Deployment Parity**: Restored `RemoteSync` functionality in the news engine for automated institutional web deployment. ✅

## 🛠 V30.4.7 News Portal Density & Reliability (2026-05-04)
- [x] **Watchlist Sorting Protocol**: Implemented session-prioritized sorting (L > PRE > AH > OVN > CLOSED) with secondary percentage-descending rank. ✅
- [x] **Watchlist Density Hardening**: Removed company descriptions from the News Portal watchlist to maximize data density. ✅
- [x] **Hardened Email Dispatch**: Upgraded `send_email` with anti-clipping UUIDs and enhanced credential validation to resolve dispatch regressions. ✅
- [x] **Dynamic Ticker Loading**: Decoupled watchlist loading from hardcoded paths; now respects `--tickers` argument for on-the-fly intelligence targeting. ✅
- [x] **Log Integrity**: Eliminated duplicate NLP and error summary log entries via singleton-pattern gates and hierarchy-leader suppression. ✅

## 🛠 V30.4 News Portal Mirror Parity (2026-05-04)
- [x] **Literal Mirror Transplant**: Achieved 100% aesthetic and logical parity by mirroring the `email_market_synopsis.py` engine into the news portal. ✅
- [x] **Email Dispatch Enabled**: Fixed the missing email trigger in the news engine; dossiers now dispatch to both web and email. ✅
- [x] **Ticker Dashboard Restoration**: Re-integrated the high-density Ticker Dashboard (Ticker Alerts) section. ✅
- [x] **Monospace !important**: Enforced strict monospace typography across all links and data fields. ✅

## 🛠 V30.4 News-Only Intelligence Restoration (2026-05-04)
- [x] **Earnings Intelligence Restoration**: Restored the 'Earnings Intelligence' section with dedicated classification logic. ✅
- [x] **Dark Gradient Background**: Enforced the authoritative Sovereign `#0f172a` to `#020617` linear gradient background. ✅
- [x] **Synopsis Restoration**: Restored the 'Institutional Synopsis' (Market Analysis Overview). ✅
- [x] **Font Fidelity Hardening**: Force-synced all news row typography to mirror the Sovereign Email (Monospace !important). ✅

## 🛠 V30.3.3 News Intelligence Hardening (2026-05-04)
- [x] **Decimal-Safe NLP**: Patched `local_nlp.py` with regex lookarounds to prevent corrupted prices (e.g., "up 0.5%") in narrative synthesis. ✅
- [x] **Institutional Styling**: Enforced Sovereign "Color School" across all news dossiers (bg-navy, gold accents, monospace metrics). ✅
- [x] **Deduplication Engine**: Implemented cross-section link tracking to ensure 0% article duplication between Macro, Semi, and Ticker sections. ✅
- [x] **3-Line Watchlist Protocol**: Deployed high-density watchlist grid with real-time valuation (MCap, P/E) and session-aware close pricing. ✅
- [x] **Session Badge Intelligence**: Integrated L/PRE/AH/OVN/C status indicators for all watchlist tickers. ✅

## 🛠 V30.3 News Intelligence Engine (2026-05-04)
- [x] **New Entry Point**: Created `news.sh` and `engine/news_market_synopsis.py` for 100% news-only reporting.
- [x] **Expanded Quotas**: Increased Macro news to 25 articles, Semi news to 15 articles.
- [x] **Ticker News Pipeline**: Implemented automated ticker-specific news fetching (max 15 total, 2/ticker) from `tickers.txt`.
- [x] **Aesthetic Alignment**: Deployed high-density "Ticker Tape" pulse bar and glassmorphism-based news lists.
- [x] **Web Deployment**: Updated `RemoteSync` to automatically deploy news dossier to `bmwseals.com/stocks/news`.

## 🛠 V30.2 Sovereign Intelligence Hardening (2026-05-02)
- [x] **Narrative Engine V2 Hardening**:
    - [x] Implement aggressive HTML stripping in `MarketSynopsisScraper` to prevent URL-split corruption.
    - [x] Expand `THEME_BLACKLIST` in `LocalIntelligenceSynthesizer` to suppress boilerplate (PERFORMANCE, SESSION, etc.).
    - [x] Add HTML entities (NBSP, URL, HTTPS) to theme blacklist to prevent focal-point pollution.
    - [x] Implement "Component Discovery" (Market Pulse, Leading Sector, Primary Catalyst).
    - [x] Integrate "Institutional Connectors" for 90%+ human-grade narrative flow.
- [x] **Verification**:
    - [x] Verify synthesis quality across all 3 market sessions (PRE/MID/POST). ✅
    - [x] Ensure no "junk" or half-info persists in the Executive Summary. ✅
    - [x] Validate end-to-end execution with zero broken links in `synopsis_preview.html`. ✅

## 🛠 V29.0 Market News Intelligence Hardening (2026-05-02)
- [x] **Synopsis Engine Overhaul**:
    - [x] Replace brittle web scraping with Resilient RSS-based synthesis.
    - [x] RSS Primary: Aggregate 100+ headlines via Google News RSS.
    - [x] Multi-Source Logic: Specialized scrapers for CNBC, Yahoo, and Edward Jones.
    - [x] Hardened EDJ Scraper: Extract high-alpha recaps while stripping IPC boilerplate. ✅
    - [x] Dynamic Synthesis: Feed raw data into Narrative Engine V2 for human-grade output.
    - [x] Implement Google News RSS integration with session-specific queries (PRE/MID/POST).
    - [x] Implement `LocalIntelligenceSynthesizer` integration to rank and summarize RSS snippets via FinVADER.
    - [x] Decommission Playwright/StealthNavigator for synopsis to reduce latency and fragility.
    - [x] Implement "Intelligence Card" source attribution for RSS-derived content.

## 🛠 V28.8 Sovereign Intelligence Hardening (2026-04-29 → 2026-05-01)

- [x] **V28.8.10 Stabilization**:
    - [x] Implement session-based gating for Edward Jones (EDJ) sources (AH only).
    - [x] Integrate source-level timestamps (`[ SOURCE @ HH:MM EST ]`) into all intelligence cards.
    - [x] Resolve 404 navigation errors in the archive by forcing absolute paths and immediate RemoteSync.
    - [x] Hardened multi-source intelligence stack with hybrid AI cache fallback.
- [x] **UI & Archival Polish (V28.8.1)**:
    - [x] Fix Sovereign Intelligence Archive 404
    - [x] Implement 48-hour rolling history ledger
    - [x] Hardened Synopsis Scraper with Multi-Source Fallback
    - [x] Deploy Institutional Archive Dashboard (archive.html)
    - [x] Transformed institutional "Web Link" to Sovereign Blue (#38bdf8) for premium interactivity. ✅
    - [x] Deployed `SynopsisArchiveManager` maintaining a rolling 48-hour historical dossier ledger. ✅
    - [x] Injected "🕰️ ARCHIVE" buttons into both Email and Web cockpit headers for historical access. ✅
- [x] **Market Synopsis Pipeline**:
    - [x] Implemented junk-pattern rejection and editorial keyword gates (V28.8.1).
    - [x] Promoted StockMarketWatch as primary PRE-market authority with signature-based extraction. ✅
    - [x] Hardened junk filter with case-insensitive patterns and navigational anchors. ✅
    - [x] Implemented dual-paragraph "Cockpit" summary for deeper pre-market insights. ✅
    - [x] Fixed global regex vulnerability where SVG <path> tags matched <p> tags. ✅
- [x] **Web Synopsis Endpoint**: Enabled automatic deployment of `synopsis_preview.html` to `bmwseals.com/email` via `RemoteSync`. ✅
- [x] **Documentation Mirror Sync**: Synchronized `.cursorrules`, `GEMINI.md`, and `CLAUDE.md` to V28 standards. ✅
- [x] **Hierarchy Leader Hardening**: Centralized logging and session authority via `market_session.py` and `error_monitor.py`. ✅
- [x] **Mirror Mandate Established**: Rules parity across all AI context files enforced. ✅
- [x] **Dependency Fix**: Add `paramiko` to `requirements.txt` to resolve `ModuleNotFoundError` for RemoteSync. ✅
- [x] **Email Synopsis Polish**: Fix trailing `nbsp; <` character corruption in Executive Summary. ✅
- [x] **Market Summary Readability**: Refactor market overview to use bulleted topics instead of run-on paragraphs. ✅
- [x] **ZeroHedge Premium Shield**: Blacklist ZH "Premium" articles from the news aggregator pipeline. ✅
- [x] **Paywall Guardian Fix**: Resolved `Errno 20` (Not a directory) in `paywall_guardian.py` by hardening zip-extraction path detection. ✅
- [x] **Intel Dashboard Enrichment**: Inject real-time Market Cap (Valuation) data into Intel Dashboard ticker rows via Yahoo Finance hydration. ✅
- [x] **Email Redesign**: Optimized HTML payload size by migrating inline styles to CSS classes (reducing size under the 102KB Gmail clip limit to 85KB) and redesigned the ticker rendering into a clean 3-line layout. ✅
- [x] **International Ticker Hardening**: Resolved data hydration regressions for international/OTC tickers (e.g., SIVE.ST / SIVEF) by resolving compound keys before fetching and deduplicating resolved symbols. ✅
- [x] **Valuation Pipeline Hardening**: Terminology standardized to `MCap:`, crisp P/E hierarchy (`'26 [9.9] '27 [11.4]`) enforced, and erroneous outliers capped at `[-500, 1000]`. ✅
- [x] **Header Aesthetic Alignment**: Centered the "REAL-TIME WATCHLIST" header and injected the authoritative "Web Link" (`bmwseals.com/stocks/email`) into the institutional header. ✅
- [x] **Data Fidelity Hardening**: Resolved $IREN valuation scaling discrepancies by prioritizing live Yahoo marketCap and hardening research-override parsing. ✅
- [x] **Institutional Header Finalization (2026-04-30)**: Confirmed `ESTABLISHED V28.8 // IDENTITY STANDARDIZED // HH:MM EST // WEB LINK` format in `compose_html`. Eliminated erroneous header injections from individual ticker tiles (`render_tile` decoupled). All 3 test suites green (Syntax + Layout + Regression). ✅

## ✅ V28.7 Intelligence Pipeline (2026-04-26)
- [x] **Log Visibility Restored**: Eliminated logging hijacking across all modules. Verified hierarchical leader logic. ✅
- [x] **Unbuffered Sync**: Forced `-u` python execution across all entry points (`run.sh`, `x.sh`, `start.bat`). Real-time terminal streaming confirmed. ✅
- [x] **Mirror Restoration**: Restored original 26-mirror nitter list from working version (936da4c). Redundancy and reliability confirmed. ✅
- [x] **Headline Sanitization**: Implemented aggressive `strip_urls` in DOM parser and standardizer to eliminate URL creep. ✅
- [x] **Rescue Path Integrity**: Verified `vxtitter` rescue logic in `vx_rescue_fetcher.py` is active and repairing broken media. ✅
- [x] **Dependency Hardening**: Installed `easyocr` and `opencv-python-headless`. Image analysis active. ✅
- [x] **SSL Resilience**: Hardened `StealthNavigator` to ignore HTTPS errors for mirror compatibility. ✅

1. - [x] **V28 Quality Gates Mandate**: Deployed Git Hooks (Ruff, Format, Conventional Commits). Fixed critical code debt across engine. Verified 100% clean pre-commit pass. ✅
2. - [x] **Deep Semi Intelligence Mandate (V28)**:
    - Hardened technical trade intelligence: Implemented 14-day lookback for SEMI sources. ✅
    - Overhauled technical documentation: Architecture, Scoring, and Specs updated. ✅
    - Deployed Git Hooks Automation: pre-commit, Ruff, and Conventional Commits. ✅
    - Automated Regression Suite: Pre-push mandatory testing enabled. ✅
    - Added direct scrape targets for technical sub-sections (Opto, PV, Markets, Micro) and Semiconductor Packaging News. Increased the mandatory section quota to **15 articles** (up to 20 available) and expanded the source ecosystem with site-specific Google News hardening.
3. - [x] **Weekend Freshness Mandate (V28)**: Integrated `MarketSession` stasis detection into `MacroAggregator`. Automatically expands the lookback window from 36h to **60h** during weekends to ensure the intelligence cockpit remains saturated despite low news flow. ✅
4. - [x] **Double-Enrichment Prevention (V28)**: Removed redundant headline tagging in `MacroAggregator`. UI enrichment is now exclusively handled by the `email_market_synopsis` layer. Fixed attribute error in scrape loop that caused Yahoo Finance feeds to crash. ✅
5. - [x] **Case-Insensitive Badge Logic (V28)**: Hardened `source_space_map` lookups with uppercase normalization. Ensures that 'DailyHunt', 'dailyhunt', and 'DAILYHUNT' all correctly resolve to 'Daily Hunt'. ✅
6. - [x] **High-Fidelity Noise Shield (V28)**: Added `FORM` to the global legitimate ticker blacklist to stop "form coalition" matches from polluting FormFactor ($FORM) pricing data. ✅
7. - [x] **FinVADER Sentiment Injection (V28)**: Integrated `finvader` pip package to permanently inject the Loughran-McDonald financial dictionary directly into the engine's VADER instance, supercharging Wall Street term awareness ("beat", "miss", "bullish"). ✅
8. - [x] **Config-First Lexicon Overrides (V28)**: Added `vader_financial_lexicon` block to `macro_config.yaml` to mathematically override and control NLP sentiment scores directly from the config. ✅
9. - [x] **Global Relevance Floor (V28)**: Added hard gate in `local_nlp.py` (`final_score < 15.0`) to drop noise articles entirely, preventing the Rotation Engine from starving and filling its quota with garbage. ✅
10. - [x] **Config-First Scoring Architecture (V28)**: Migrated ALL scoring data (keywords, feeds, tickers, bonus terms, cluster multipliers) from hardcoded Python to `config/macro_config.yaml`. Implemented bonus keywords (variable-point), cluster multiplier (1.4x for 2+ co-occurring terms), and billion-scale regex detection (+45). Added 3 new niche feeds (SemiEngineering, Google News CPO/Transceiver). 132 keywords, 18 bonus terms, 25 feeds, 30 tickers now config-driven. ✅
2. - [x] **Temporal Hierarchy Mandate (V28)**: Established `engine/market_session.py` as the absolute authority for market calendar/session logic. Refactored `live_prices.py` and `email_market_synopsis.py` to use hierarchy gates, effectively stopping "Zombie Fetches" on weekends.
3. - [x] **News Signal Hardening (V28)**: Implemented institutional source normalizer, 4-word title floor, and opinion/clickbait gate. Expanded blacklist (Buffett, Savage).
4. - [x] **Subscription & Relevance Hardening (V28)**: 100% block on Bloomberg, WSJ, Seeking Alpha, and Barron's. Implemented Video Purge and Geographic Relevance Gate.
5. - [x] **News Hardening Mandate (V28)**: Implemented 100% block on AOL/MSN/Motley Fool domains. Added 36h hard freshness gate and 24h score decay.
6. - [x] **Language & Personality Filtration (V28)**: Hardened blacklist for Pelosi, Cramer, Ramsey and implemented non-English news gate.
7. - [x] **News Aesthetic Mandate (V28)**: Implemented alternating blue/green tile backgrounds for the news dossier.
8. - [x] **Cache Mandate (V28)**: Enforced 15-minute global TTL by removing `force=True` in synopsis engine and adding countdown telemetry to `live_prices.py`.
9. - [x] **Technical Documentation (V28)**: Generated `ARCHITECTURE_DEEP_DIVE.md` and `INTELLIGENCE_SCORING.md` technical references.
10. - [x] **Decoupled Pricing Math (V28)**: Separated `close_price` and `ext_price` in the Performance Movers list to prevent clobbering.
11. - [x] **Pricing Math Test Suite (V28)**: Deployed `tests/test_pricing_math.py` to ensure math fidelity in session-aware rendering.
12. - [x] **Unified Test Runner (V28)**: Created `run_all_tests.py` to aggregate logic, layout, and integration tests.
13. - [x] **"Always Run" Mandate (V28)**: Integrated mandatory test gating into `start.bat`.
14. - [x] **Test Suite Repair (V28)**: Restored 33+ failing tests and fixed AH/PM label consistency.
15. - [x] **Single-Line Row Protocol (V28)**: Enforced `white-space: nowrap` and purged `<br/>` tags.
16. - [x] **Ticker Suffix Recovery (V28)**: Implemented automated `.TW` -> `.TWO` retry logic in `live_prices.py` to resolve Taiwan exchange data gaps.
17. - [x] **Universe Expansion (V28)**: Integrated 57 new high-conviction tickers from `research/additional_plays.md` into the master CSV and JSON databases.
18. - [x] **Hierarchy Leader Error Monitor (V28)**: Deployed `engine/error_monitor.py` as the central authority for error tracking. Integrated into all core scripts via `atexit` to ensure a unified error summary is printed at the very end of execution.
19. - [x] **V28 Sovereign Engine Hardening**:
    - Synchronized `stealth_navigator.py` and `intelligence_engine.py` to V28.
    - Resolved `ModuleNotFoundError` by hardening imports across `yahoo_auth.py`, `live_prices.py`, and `news_fetcher.py`.
    - Fixed `PipelineOrchestrator` momentum key mismatch (`recent_7d_list`).
    - Restored `Regression Suite (Pytest)` pass rate by aligning `test_news_hardening.py` and `test_modular_engine.py` with V28 session-aware logic.
20. - [x] **Data Hydration (V28)**: ✅ COMPLETE — `openbb_fetcher.py --force` run across full 201-ticker universe. 170 updated, 31 skipped (invalid tickers: `2027`, `400G`, `1.6T`, etc.). All valid tickers now have `recent_7d_status`.
21. - [x] **Regression Suite Fully Restored (V28)**: **158/158 tests passing**. Fixed 7 test-side issues: import paths, session boundary timezone, legacy `PM` label, config-driven source names, historical data tolerance, dist artifact checks, and F&G live value assertions.
22. - [x] **CNBC Source Normalization (V28)**: Hardened `source_space_map` to catch generic "WORLD" and "Top News" badges from CNBC RSS feeds and map them to "CNBC".
23. - [x] **Error Monitor Hardening (V28)**: Updated `error_monitor.py` to always output an explicit `Total [ERRORS] = $NUM` badge at the end of every run. Idempotency verified.
24. - [x] **Log Conciseness & Formatting (V28)**: Consolidated dispatch logs in `email_market_synopsis.py`. Errors now display first, followed by intelligence and timestamped confirmation. Redundant shell-level time stamps suppressed by internalizing confirmation.
25. - [x] **Hardened News Deduplication (V28)**: Deployed "Entity Intersection" heuristic in `MacroAggregator` and `LocalIntelligenceSynthesizer`. Catching near-duplicates that share rare subjects (e.g., 'Aeluma') even when Jaccard overlap is low.
26. - [x] **Log Stability Fix (V28)**: Resolved a type mismatch (`frozenset` vs `tuple`) in the news deduplication logic that was causing crashes in Yahoo Finance scrape paths.
27. - [x] **High-Fidelity SEMI Expansion (V28)**: Added SemiAnalysis RSS and hardened Semiconductor Digest (via Google News fallback). Increased SEMI news quota to 20 articles (with 10-article mandatory minimum) and deployed the "II. HIGH-FIDELITY SEMI INTELLIGENCE" section.
28. - [x] **ZeroHedge Hardening (V28)**: Decommissioned general firehose. Targeted scraping of /markets, /tech, /energy, /econ verticals now standard.
29. - [x] **NLP Fidelity Upgrades (V28)**: Deployed 'Consumer Fluff' (-15.0) and 'Litigation' (-25.0) penalties. Added +10.0 'Sector Alpha' bonus for institutional signals (Goldman, Hedge Funds).
30. - [x] **Unified Intelligence Sort (V28)**: Decommissioned binary rotation engine. Deployed a **Unified Sort with Freshness Bonus (+10.0)** to prevent fresh junk from displacing stale alpha.
31. - [x] **SemiAnalysis 403 Bypass (V28)**: Resolved HTTP 403 blocking on SemiAnalysis Substack by deploying a Google News search RSS fallback with a 7-day lookback window.
32. - [x] **Stability Fix (V28)**: Resolved `NameError` in `email_market_synopsis.py` by aligning status logic with the Unified Sort architecture.
33. - [x] **Institutional Aesthetic Upgrade (V28)**: Complete visual redesign of the Market Intelligence dossier. Implemented an institutional-grade header system with `letter-spacing: 4px`, `font-weight: 900`, and gold accents. Transitioned to a premium linear gradient background (`#0f172a` to `#020617`) matching the user's "View I love" reference. Verified via `tests/test_header_aesthetic.py`. ✅
