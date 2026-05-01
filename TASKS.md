## 🛠 V28.8 Sovereign Intelligence Hardening (2026-04-29 → 2026-05-01)
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
8. - [x] **Config-First Scoring Architecture (V28)**: Migrated ALL scoring data (keywords, feeds, tickers, bonus terms, cluster multipliers) from hardcoded Python to `config/macro_config.yaml`. Implemented bonus keywords (variable-point), cluster multiplier (1.4x for 2+ co-occurring terms), and billion-scale regex detection (+45). Added 3 new niche feeds (SemiEngineering, Google News CPO/Transceiver). 132 keywords, 18 bonus terms, 25 feeds, 30 tickers now config-driven.
9. - [x] **Temporal Hierarchy Mandate (V28)**: Established `engine/market_session.py` as the absolute authority for market calendar/session logic. Refactored `live_prices.py` and `email_market_synopsis.py` to use hierarchy gates, effectively stopping "Zombie Fetches" on weekends.
10. - [x] **News Signal Hardening (V28)**: Implemented institutional source normalizer, 4-word title floor, and opinion/clickbait gate. Expanded blacklist (Buffett, Savage).
11. - [x] **Subscription & Relevance Hardening (V28)**: 100% block on Bloomberg, WSJ, Seeking Alpha, and Barron's. Implemented Video Purge and Geographic Relevance Gate.
12. - [x] **News Hardening Mandate (V28)**: Implemented 100% block on AOL/MSN/Motley Fool domains. Added 36h hard freshness gate and 24h score decay.
13. - [x] **Language & Personality Filtration (V28)**: Hardened blacklist for Pelosi, Cramer, Ramsey and implemented non-English news gate.
14. - [x] **News Aesthetic Mandate (V28)**: Implemented alternating blue/green tile backgrounds for the news dossier.
15. - [x] **Cache Mandate (V28)**: Enforced 15-minute global TTL by removing `force=True` in synopsis engine and adding countdown telemetry to `live_prices.py`.
16. - [x] **Technical Documentation (V28)**: Generated `ARCHITECTURE_DEEP_DIVE.md` and `INTELLIGENCE_SCORING.md` technical references.
17. - [x] **Decoupled Pricing Math (V28)**: Separated `close_price` and `ext_price` in the Performance Movers list to prevent clobbering.
18. - [x] **Pricing Math Test Suite (V28)**: Deployed `tests/test_pricing_math.py` to ensure math fidelity in session-aware rendering.
19. - [x] **Unified Test Runner (V28)**: Created `run_all_tests.py` to aggregate logic, layout, and integration tests.
20. - [x] **"Always Run" Mandate (V28)**: Integrated mandatory test gating into `start.bat`.
21. - [x] **Test Suite Repair (V28)**: Restored 33+ failing tests and fixed AH/PM label consistency.
22. - [x] **Single-Line Row Protocol (V28)**: Enforced `white-space: nowrap` and purged `<br/>` tags.
23. - [x] **Ticker Suffix Recovery (V28)**: Implemented automated `.TW` -> `.TWO` retry logic in `live_prices.py` to resolve Taiwan exchange data gaps.
24. - [x] **Universe Expansion (V28)**: Integrated 57 new high-conviction tickers from `research/additional_plays.md` into the master CSV and JSON databases.
25. - [x] **Hierarchy Leader Error Monitor (V28)**: Deployed `engine/error_monitor.py` as the central authority for error tracking. Integrated into all core scripts via `atexit` to ensure a unified error summary is printed at the very end of execution.
26. - [x] **V28 Sovereign Engine Hardening**:
    - Synchronized `stealth_navigator.py` and `intelligence_engine.py` to V28.
    - Resolved `ModuleNotFoundError` by hardening imports across `yahoo_auth.py`, `live_prices.py`, and `news_fetcher.py`.
    - Fixed `PipelineOrchestrator` momentum key mismatch (`recent_7d_list`).
    - Restored `Regression Suite (Pytest)` pass rate by aligning `test_news_hardening.py` and `test_modular_engine.py` with V28 session-aware logic.
27. - [x] **Data Hydration (V28)**: ✅ COMPLETE — `openbb_fetcher.py --force` run across full 201-ticker universe. 170 updated, 31 skipped (invalid tickers: `2027`, `400G`, `1.6T`, etc.). All valid tickers now have `recent_7d_status`.
28. - [x] **Regression Suite Fully Restored (V28)**: **158/158 tests passing**. Fixed 7 test-side issues: import paths, session boundary timezone, legacy `PM` label, config-driven source names, historical data tolerance, dist artifact checks, and F&G live value assertions.
29. - [x] **CNBC Source Normalization (V28)**: Hardened `source_space_map` to catch generic "WORLD" and "Top News" badges from CNBC RSS feeds and map them to "CNBC".
30. - [x] **Error Monitor Hardening (V28)**: Updated `error_monitor.py` to always output an explicit `Total [ERRORS] = $NUM` badge at the end of every run. Idempotency verified.
31. - [x] **Log Conciseness & Formatting (V28)**: Consolidated dispatch logs in `email_market_synopsis.py`. Errors now display first, followed by intelligence and timestamped confirmation. Redundant shell-level time stamps suppressed by internalizing confirmation.
32. - [x] **Hardened News Deduplication (V28)**: Deployed "Entity Intersection" heuristic in `MacroAggregator` and `LocalIntelligenceSynthesizer`. Catching near-duplicates that share rare subjects (e.g., 'Aeluma') even when Jaccard overlap is low.
33. - [x] **Log Stability Fix (V28)**: Resolved a type mismatch (`frozenset` vs `tuple`) in the news deduplication logic that was causing crashes in Yahoo Finance scrape paths.
34. - [x] **High-Fidelity SEMI Expansion (V28)**: Added SemiAnalysis RSS and hardened Semiconductor Digest (via Google News fallback). Increased SEMI news quota to 20 articles (with 10-article mandatory minimum) and deployed the "II. HIGH-FIDELITY SEMI INTELLIGENCE" section.
35. - [x] **ZeroHedge Hardening (V28)**: Decommissioned general firehose. Targeted scraping of /markets, /tech, /energy, /econ verticals now standard.
36. - [x] **NLP Fidelity Upgrades (V28)**: Deployed 'Consumer Fluff' (-15.0) and 'Litigation' (-25.0) penalties. Added +10.0 'Sector Alpha' bonus for institutional signals (Goldman, Hedge Funds).
37. - [x] **Unified Intelligence Sort (V28)**: Decommissioned binary rotation engine. Deployed a **Unified Sort with Freshness Bonus (+10.0)** to prevent fresh junk from displacing stale alpha.
38. - [x] **SemiAnalysis 403 Bypass (V28)**: Resolved HTTP 403 blocking on SemiAnalysis Substack by deploying a Google News search RSS fallback with a 7-day lookback window.
39. - [x] **Stability Fix (V28)**: Resolved `NameError` in `email_market_synopsis.py` by aligning status logic with the Unified Sort architecture.
41. - [x] **Institutional Aesthetic Upgrade (V28)**: Complete visual redesign of the Market Intelligence dossier. Implemented an institutional-grade header system with `letter-spacing: 4px`, `font-weight: 900`, and gold accents. Transitioned to a premium linear gradient background (`#0f172a` to `#020617`) matching the user's "View I love" reference. Verified via `tests/test_header_aesthetic.py`. ✅
42. - Date: 2026-04-26

# Project Status — April 25, 2026
## 🚀 Version: V28 (Config-First & FinVADER Architecture)

Status: **PRODUCTION DEPLOYED — HARDENED**

📊 **Project Status: Sovereign Intel**
- **Current Tier**: V28 (Config-First & FinVADER Architecture)
- **Critical Progress**: Injected `FinVADER` financial lexicons into the NLP engine. Relocated all remaining Python hardcoded variables directly into `macro_config.yaml`. Hardened semiconductor intelligence with direct scrape targets and increased mandatory quota to **15 articles**. Established **Global Relevance Floor** to prevent quota starvation on weekends.
- **Next Milestone**: Validate new semi feeds and 15-article quota density in Monday's market opening dossier.
- Date: 2026-04-25

### 🚀 Previous Status: V28 — Sovereign Intelligence Hardening (Futures Divergence)
- [x] **Index Divergence Pulse**: Integrated comparative row-tracking for all major US indices. Shows **Friday Cash Close** vs. **Sunday Night Futures** side-by-side to highlight market opening sentiment.
- [x] **Futures Support**: Added active tracking for `NQ=F` (Nasdaq), `ES=F` (S&P 500), and `YM=F` (Dow 30).
- [x] **Comparative UI**: Redesigned the Pulse block into high-contrast comparative tiles with directional background chips.
- [x] **International Ticker Shield**: Enhanced regex to capture dot-suffixed tickers (`LPK.DE`, `SOI.PA`, etc.).
- [x] **Universal Gold Protocol**: Standardized symbol linking in brand gold to prevent blue auto-links.
- Date: 2026-04-19

### 🚀 Previous Status: V28 — Sovereign Intelligence Hardening (Desktop UX)
- [x] **Global Market Normalization**: Balanced tile sizes for HSI, Nikkei, DAX, FTSE to match US Pulse tiles on desktop.
- [x] **Description Visibility**: Extended description truncation (240 chars) and brightened note color (`#64748b`) for professional legibility.
- Date: 2026-04-19

### 🚀 Previous Status: V28 — Sovereign Intelligence Hardening (Content Quality)
- [x] **Momentum Velocity Block-Formatting**: Refactored momentum chips into block-level tiles for multi-device readability.
- [x] **Data-Void Hydration**: Added a sector-wide scan to automatically identify and fill price gaps in the intelligence universe.
- Date: 2026-04-19

### 🚀 Previous Status: V22.10 — Sovereign Intelligence Stability
- [x] **Dynamic Price Recovery**: Restored high-fidelity ticker discovery and real-time price flair injection.
- [x] **Massive Symbol Bridge**: Integrated S&P 500 + Russell 2000 (3,100+ mappings).
- [x] **15-Minute Restraint**: Hardened cache TTL to 900s for conservative Yahoo API usage.
- [x] **Production Leak Hardening**: Blacklisted `CEO`, `IRA`, `NV`, `SAVE`, `LAYER`, etc.
- [x] **Recursive Aliasing**: Resolved `KLA->KLAC`, `BMW->BMWYY`, `IPG->IPGP` for headline narratives.
- [x] **Zero-Silence Protocol**: Suppress broken chips/leaks in narratives.
- [x] **Smart Aliasing**: Pivot from names (Nvidia) to tickers (NVDA) automatically.
- [x] **Cross-Correlative Prioritization**: Narrative synthesis now led by Alpha (1.5x) and Hiddenness (0.8x) scoring.
- [x] **Adaptive Lexicon Biasing**: VADER sentiment analyzer now weights tokens based on real-time Fear & Greed vibes.
- [x] **NER Entity Discovery**: Lightweight NLTK pipeline identifies unmapped organization catalysts in headlines.
- [x] **Token Efficiency**: Redundant RSS descriptions cleaned and summarization window optimized.
- Date: 2026-04-19

### 🚀 Previous Status: V22.1 — Documentation & Hardening
- [x] **Documentation Overhaul**: Upgraded `SOVEREIGN_INTEL_SYSTEM.md` with high-fidelity Mermaid architecture and technical specifications.
- [x] **NLP Pipeline Mapping**: Documented LSA, TF-IDF, and VADER logic for future parity.
- [x] **Hardening Guide**: Captured anti-clipping and deduplication protocols.
- Date: 2026-04-19

### 🚀 Previous Status: V22.0 — Local NLP Intelligence & Autonomous Dossiers
- [x] **Local NLP Engine**: Deployed `engine/local_nlp.py` using VADER (Sentiment), Sumy (Summarization), and TF-IDF (Keywords).
- [x] **Autonomous Synthesis**: Refactored `email_market_synopsis.py` to generate distinct 80%-unique Market and Sector overviews.
- [x] **Aesthetic Hardening**: Implemented liquid-table layout with hyperlinked headlines and color-coded `$TICKER` price injection.
- [x] **Dual Stream Intelligence**: Separated Market RSS headlines from Monitoring news to prevent data overlap.
- [x] **Hot-Fetch Integration**: Macro index prices ($BTC, $NQ, etc.) now auto-hydrate inside the email loop using root `live_prices` engine.
- Date: 2026-04-19

### 🚀 Previous Status: V21.0 — Modular Pipeline & High Density Web endpoints
- [x] **Triple-Layer Sync**: Deployed `engine/sync_triple.py` (Tweets + News + OCR) and unified the `terminal.py` conductor.
- [x] **Documentation**: Generated `docs/SYNC_GUIDE.md` explaining the update cycle and recommendations.
- [x] **Pipeline Integrity**: Deployed `tests/verify_integrity.py` for automated syntax and Windows encoding (UTF-8) audits.
- [x] **Dual Deployment**: Hardened `PipelineOrchestrator` to simultaneously update `/web/semi` and `/web/ai`.
- **Modular Refactor**: Migrated all Semi/AI assets to `/web/*` and consolidated core logic in Root.
- **Unified Orchestration**: Global `PipelineOrchestrator` automates News, Prices, OBB, and Deployment.
- **Yahoo Stealth**: Decoupled Auth (`engine/yahoo_auth.py`) + `chrome146` TLS Handshake (Max Supported).
- **AI Terminal**: Hardened 100% data coverage for ADRs/Small-caps; fixed legacy path drift.
- [x] **AI Terminal Integrity**: Restored 100% dynamic Alpha scoring (math-driven); fixed OpenBB data clobbering to restore Analyst/Institutional/Short counts.
- [x] **AI Terminal Mapping**: Repaired Ticker-to-Company mapping to prioritize Actual Company Names (e.g. Terrestrial Energy) over raw symbols.
- [x] **Data Cross-Pollination**: Refactored `openbb_fetcher.py` and `PipelineOrchestrator` to synchronously enrich both Terminals.
- [x] **Reliability**: 55+ tests passing; automated regression checks for modular paths.
- **Deployment**: Unified SFTP sync for modular directory nesting.
- Date: 2026-04-18

- **Modular Engine**: Migrated scoring and aggregation logic to `engine/` for high reuse.
- **Dynamic Intelligence**: Upside, MCAP, and P/E metrics now pulled from master DB with zero placeholders.
- **AI Dashboard Fidelity**: Patched `PipelineOrchestrator` to automatically map legacy research keys (`Company Name`, `Role / Notes`).
## Recent UI Hardening (V22.49)
- **News Link Purge**: Removed all internal news titles links; dossier now focuses exclusively on Yahoo Finance price discovery.
- **Global Market Visibility**: Hardened HSI/Nikkei tiles. `CLOSED` status is now bold Red. Percentages upsized to 15px with directional background chips.
- **Ticker Standard**: All symbols ($TICKER) now use `@f59e0b` (Gold) and link directly to Yahoo Finance.
- **Typography Alignment**: Eliminated `monospace` drift in Macro and Momentum sections.

- **Image Pipeline**: OCR → `processed_images.json` → `visual_intel[]` per post → `visual_mentions` in master.
- **Dashboard**: Visual buzz (📷) badges alongside tweet buzz (𝕏) in buzz bar + row chips.
- **Scraper Safety**: `visual_intel` now survives `_deduplicate_file` and `_incremental_save` rewrites.
- **Orchestration**: `x_intel_daily_sync.py` auto-runs image_analyzer + visual_buzz_aggregator post-scrape.
- **Durability**: `rebuild_master()` now carries forward `visual_mentions` — OCR work never lost on rebuild.
- **Unicode**: All JSON writes use `ensure_ascii=True` — no more VS Code ambiguous-unicode warnings.
- **Logging**: Python scripts now autonomously output to `logs/*.log` to prevent debugging noise.
- **Scraper Search**: Fixed Nitter date constraint parsing to prevent recursive vintage deep fetches.
- **Spam Filter**: Yahoo News Anti-Spam (strict ticker matching) logic deployed and DB scrubbed (751 items removed).
- **Quality**: 7-day lookback filtering active for news sanity.
- **Deduplication**: SHA-256 Title-based news deduplication verified.
- **Testing**: `test_news_fetcher` updated for async+playwright stealth logic execution.
- **Dashboard**: Fixed `#` column centering/cut-off + 7-day momentum dots (Green/Red) on both root and AI terminals.
- Date: 2026-04-18
- **AI Terminal**: Consistently consolidated Ticker + Company + Momentum into a single column.
- **AI Terminal**: Implemented Case-Insensitive filtering (toUpperCase) for Sectors and Exchanges.
- **AI Terminal**: Hardened `LIVE_PRICES` data binding to fix "Day $" and "% Chg" display issues.
- **Sync**: Automated SFTP upload enabled for both root and AI `live_prices.py` scripts.
- **Scoring**: Deployed percentile-based Intelligence Engine for Alpha/Risk/Hidden metrics.
- **Root Terminal**: Merged Company column under Ticker (same as AI terminal): Ticker → Company name → 7-day momentum strip.
- **Root Terminal**: Added `getExchAbbrev()` — exchange names now display as abbreviations (NSQ, NYSE, OTC, TSE, TPEX, etc.).
- **Root Terminal**: Fixed `todayChg` to read `live.price_chg` (was `live.change` — causing blank Day $ column).
- **Root Terminal**: Momentum strip now reads from `e.obb.recent_7d_status` (openbb_supplement) as primary — correct green/red bars.
- **AI Terminal**: Fixed `todayChg`, `obb`, and `p` mappings to use `live.price_chg`, `h.openbb_supplement`, `entry.performance`.
- **Data Integrity**: Renamed `4062.T → 4062.T / IBIDY` and `7912.T → 7912.T / DNPLY` in master DB to surface US ADR symbols.
- **Data Integrity**: Force-fetched `recent_7d_status` + `perf_1y` for 3105.TWO, 7912.T, 4062.T — all now show correct momentum + 1Y return.
- **Data Discovery**: Full 113-ticker data audit run — restored `performance{}` for all tickers with `history` and `1y` data.
- **Pipeline**: Fixed `NameError` in `remote_sync.py` `__main__` block (was calling bare `sync()` instead of `RemoteSync.sync()`).
- **Pipeline**: Fixed `PipelineOrchestrator` to pull from `AI_MASTER_DATA.json` instead of raw research file, restoring momentum/financials to AI terminal.
- **Pipeline Integrity**: Automated syntax and non-ASCII audit check installed to prevent Windows terminal crashes.
- Date: 2026-04-18
- **Yahoo Stealth Protocol (V19.5)**: Decoupled authentication logic from extraction loops. `engine/yahoo_auth.py` now harvests and caches session crumbs/cookies via Playwright, providing them to lightweight `curl_cffi` clients.
- **Yahoo Stealth Protocol (V19.5)**: Standardized Chrome 147.0.7727.101/105/110 identity across all scripts.
- **Yahoo Stealth Protocol (V19.5)**: Implemented randomized "human" batching (8-13 units per burst, 3.3s-10s delay).
- **Yahoo Stealth Protocol (V19.5)**: Updated `openbb_fetcher.py` and `news_fetcher.py` to use the unified stealth session, eliminating `yfinance` 401 blocks.
- **Yahoo Stealth Protocol (V19.5)**: Audited all `curl_cffi` instances to ensure `chrome147` handshake integrity.

---

## 🛠 Active Tasks

- [x] **Task 2: Expanded X Search Filtering** — Added Username select and Date From/To inputs to dashboard; updated `x_intel_deep_scraper.py` with CLI flags (`--since`, `--until`, `--query`).
- [x] **Task 3: Username Management Script** — Created `engine/manage_users.py` and `database/monitored_users.json` for dynamic user tracking.
- [x] **Task 4: BetterTwitFix Integration** — Implemented `engine/vx_rescue_fetcher.py` and integrated into scraper as a fallback repair layer for truncated/broken tweets.
- [x] **Task 5: Image Intelligence Hardening** — Removed OCR batch limits in `image_analyzer.py`; modernized `visual_buzz_aggregator.py` to handle all monitored users dynamically.
- [x] **Task 6: Unified Terminal** — Created `terminal.py` menu system for orchestrating all 11 engine scripts.
- [x] **Task 13F: Institutional Alpha** — Created `engine/inst_13f_fetcher.py` to pull 13F hedge fund positioning (WhaleRock, Altimeter, Coatue) into master data.
- [x] **Task LIDE: Glass Supercycle Mapping** — Created `engine/glass_intel_mapper.py` to map the LIDE/TGV supply chain (LPKF, Absolics, Corning) into the terminal.

---

## ✅ Completed — V15.4 Pipeline Durability + Unicode (2026-04-14)

## ⚡ Market Intelligence (Email Synopsis)

- [x] **V4.3.1 Architecture (Architect Edition)**: Implemented Sovereign Pulse Bar and Narrative Synthesis.
- [x] **Live Macro Integration**: Automated Yahoo Finance RSS feed for global headlines.
- [x] **Ticker Injection**: Formatted chips ($META, $AVGO) now inject prices into news sentences.
- [x] **Strategic Segmentation**: Separate section for Private/Pre-IPO vetting (Celestial AI, etc.).
- [x] **Live/Current Market Price Scraper**: Automate the price for BTC, ETH, Nasdaq, S&P 500, DOW. Last 24 hours % up/down for BTC/ETH and full $ prices.
- [x] **Live Sentiment Scraper**: Automate the `feargreedmeter.com` scrape for Market and Crypto.
- [x] **Ticker Discovery Wrapper**: Hardened the loop to call `live_prices.py` for unknown news mentions.
- [x] **NLP Synthesis**: Integrated offline local summarization (LSA) and keyword extraction (TF-IDF).
- [ ] **Automation Logic**: Configure Windows Task Scheduler for 7:30 AM / 4:30 PM delivery.

- [x] **Merge ISSUES.md into TASKS.md**: Integrated historical issues and cleared ISSUES.md.
- [x] **Unicode fix (all writers)**: `ensure_ascii=False` → `True` in `rebuild_master.py`,
  `visual_buzz_aggregator.py`, and both write paths in `x_intel_deep_scraper.py`.
  All JSON files are now pure 7-bit ASCII; emojis/smart-quotes encoded as `\uXXXX`.
  Eliminates VS Code "ambiguous unicode characters" warning permanently.
- [x] **Durability fix — `rebuild_master.py`**: Now reads existing master's `visual_mentions`
  + `visual_last_updated` before overwriting. OCR aggregation data survives every rebuild.
- [x] **Durability fix — `x_intel_deep_scraper.rebuild_master()`**: Same carry-forward logic
  applied to the inline version called after each scrape run.
- [x] **`scratch/verify_pipeline.py`**: Quick sanity script — checks unicode, visual_mentions,
  intel.js, processed_images.json, and per-user visual_intel. Run any time to confirm health.
- [x] **Verified clean**: 6507 posts | 37 visual tickers | 560 OCR log entries | ALL CLEAR.
- [x] **Nitter Search Bug**: Switched literal `+` parameters to `%20` encoded spaces in deep scraper. Search queries `since` and `until` commands are now successfully enforced by nitter instead of ignored, stopping infinite loops fetching old tweets.
- [x] **Autonomous Audit Logging**: Scripts `x_intel_instant_sync.py`, `x_intel_daily_sync.py`, `x_intel_deep_scraper.py`, `x_intel_fetcher.py`, and `x_intel_auto_sync.py` now all execute FileHandlers sending debugging telemetry directly to `logs/` directory autonomously.

---

## 🐞 Historical Issues & Resolutions (from ISSUES.md)

- **[FIXED] BeautifulSoup/Playwright Missing Dependencies**: Scrapers failed on fresh Windows nodes.
  - **Resolution**: Created global `requirements.txt` and integrated `python -m playwright install chromium`.
- **[FIXED] Windows I/O Unicode Crash**: `ValueError: I/O operation on closed file` during translation.
  - **Resolution**: Implemented `io.TextIOWrapper` with error handling in `translate_intel.py`.
- **[FIXED] Ticker Fragmentation**: Mirror HTML caused $N V D A$ instead of $NVDA.
  - **Resolution**: Deployed V11.0 Surgical Regex with boundary detection.
- **[FIXED] Browser CORS Security Block**: Browser prohibits `fetch()` from local filesystem.
  - **Resolution**: Implemented JS Data Bridge (`research/sync_data.py`).
- **[OPEN] Data Gaps**: Revenue estimates for Tier-2 suppliers (AXTI, Sumitomo) are estimates.
  - **Status**: Research ongoing.

---

## ✅ Completed — V15.3 Visual Intelligence Pipeline (2026-04-14)

- [x] **China-only reclassification**: INNO (InnoLight) + EOPT (Eoptolink) → `Bucket: Private`,
  `Status: China-Only`, `no_dashboard: true`. Excluded from scoring, rankings, and price fetches.
  Remain in Private watchlist section for research tracking.
- [x] **Image processing forensic**: Confirmed 560/2517 total images processed overnight.
  1,957 remaining images are new from tonight's scrape (not data loss — genuinely new downloads).
  `processed_images.json` is the durable skip-log; `visual_intel[]` per-post arrays are intact.
- [x] **`_deduplicate_file()` fix**: Now explicitly sets `visual_intel: []` on all posts,
  ensuring OCR data never silently evaporates through dedup or incremental save passes.
- [x] **`_incremental_save()` fix**: Merges `visual_intel` from existing posts by ID when
  combining new + existing post lists.
- [x] **`engine/visual_buzz_aggregator.py`**: New engine module — reads all `x_intel_<user>.json`
  `visual_intel[]` arrays, aggregates ticker OCR hits, merges `visual_mentions` dict into
  `x_intel_master.json` + rebuilds `intel.js`. First run: 684 hits across 555 images, 37 tickers.
- [x] **`x_intel_daily_sync.py` pipeline**: Post-scrape auto-runs Step 2 (image_analyzer OCR)
  + Step 3 (visual_buzz_aggregator) so every nightly run is fully self-contained.
- [x] **Dashboard — `no_dashboard` filter**: `buildEntries()` now skips entries with
  `no_dashboard: true` — INNO/EOPT never appear in ranked table or scoring.
- [x] **Dashboard — Visual buzz badges**: 📷 green badge added to row Role/Notes cell showing
  image hit count (alongside existing 𝕏 tweet buzz gold badge). Tooltip shows OCR sample text.
- [x] **Dashboard — Buzz bar upgraded**: `renderBuzz()` now merges tweet buzz (𝕏N) + visual
  mentions (📷N) into unified top-14 ranking. Both signal types visible per tag.

---

## ✅ Completed — V15.2 AH/PM Extended-Hours Column (2026-04-14)

- [x] **`live_prices.py`**: Capture `postMarketPrice`/`postMarketChangePercent` + `preMarketPrice`/`preMarketChangePercent` from Yahoo quote response (zero extra requests — same batch call). Stored as `ext_price`, `ext_pct`, `ext_type` (AH/PM).
- [x] **`cpo_plays.html`**: Added **AH / PM** column (sortable) showing label, ext price, and % move in green/red.
- [x] **Micro-timestamp**: `HH:MMZ` update time displayed above regular price cell so staleness is visible at a glance.
- [x] **Colspan**: Private watchlist divider bumped 16→17.
- [x] **Sort**: `ext` key wired into `sortFn` for AH/PM column sort.

---

## ✅ Completed — V15.1 Filter Integrity Sprint (2026-04-14)

### Bug Fixes (cc429cc)
- [x] **CRITICAL: Duplicate function definitions removed** — `filterIntel()`, `openIntelModal()`,
  `closeIntelModal()`, and `renderBuzz()` were defined TWICE in `cpo_plays.html` (lines 620+648).
  The second stub version silently overrode the correct first definition, breaking the Intel modal.
- [x] **P/E Filter — Sentinel bug fixed** — `pe26=999` / `pe27=999` are the sentinel for "no EPS data".
  Old code: `e.pe26 < state.maxPe26` incorrectly excluded no-data stocks when any filter was active.
  New code: max filter active → exclude 999; min-only filter → allow 999 through.
- [x] **OBB null-safe access** — `e.obb.inst_ownership_pct` crashed on stocks with no OBB data.
  Replaced with null-safe pattern + `hasInst`/`hasShort`/`hasAnalysts` guards.
- [x] **Buzz count parseInt** — `sfloat(e.buzz?.['7d'])` was parsing buzz counts as floats.
  Changed to `parseInt(..., 10)` to correctly handle integer mention counts.

### QA (2026-04-14)
- [x] **`tests/test_dashboard_filters.py` created** — 29 new tests covering:
  - `TestPEFilterLogic` (8 tests) — sentinel, range, min-only, regression
  - `TestOBBNullSafeFiltering` (8 tests) — null obb, empty string, range checks
  - `TestBuzzFilterParsing` (5 tests) — int string, raw int, None, zero, out-of-range
  - `TestHTMLStructuralIntegrity` (8 tests) — regex scan of actual HTML for duplicate defs,
    parseInt presence, hasInst/hasShort/hasAnalysts presence, 999 sentinel presence
- [x] **Full test suite: 50 tests — 100% passing**

---

## ✅ Completed — V15.0 Surgical Integrity (2026-04-14)

- [✅] Forensic: V11.0 Surgical Repair (Fixed Ticker Fragmentation & Word-Smashing)
- [✅] Dependency: Validated 100% environment compatibility via `requirements.txt`.

## Dashboard UI & Readability (V13.2)
- [x] Convert X-Intelligence Buzz Bar to horizontal orientation
- [x] Increase global font sizes for high-res desktop readability (11px -> 13px)
- [x] Fix vertical text issues in social intelligence search results
- [x] Execute UI/UX Accessibility Audit

## QA & Stability
- [x] Restore and standardize the automated test suite
- [x] Resolve test-collection errors and module pathing issues
- [x] Sync localized forensic logic with regression tests
- [x] Verify remote production webpage (bmwseals.com/stocks/)
- [x] Write QA tests for passesFilters() filter logic (P/E, OBB, Buzz, Duplicate Defs)

---

## 🔜 Open / Backlog

- [x] **INNO/EOPT Country tag fix** (2026-04-14): INNO corrected to `Country: China` — yfinance
  ticker "INNO" resolves to wrong NYSE entity; financials cleared, `no_yfinance: true` flagged.
  EOPT corrected to `Country: China`, `currency: CNY`, `real_ticker: 300502.SZ`. Both master
  JSON and `dashboard_data.js` updated.
- [x] **HBM4 Supply Chain Audit**: Expanded glass substrate mapping to include HBM4-specific interposers and back-end packaging (Besi, ASM Pacific).
- [x] **Automated Institutional Scoring**: Factored 13F conviction counts straight into the Alpha ranking algorithm in JS (`cpo_plays.html`).
- [x] **Real-time Price Engine 2.0**: Validated `live_prices.py` correctly fetches non-USD ADR equivalents (BESIY, ASMVY).

---

[✅] **Translation Cache**: Persistent `translation_cache.json` for zero-waste repeated runs.
[✅] **Remote Sync**: Automated SFTP deployment for production mirroring.
[✅] **GIGACPO BRAIN**: Updated SiPh/CPO master intelligence bridge.
[✅] **Filter QA**: 50-test automated regression suite covering core dashboard logic.
