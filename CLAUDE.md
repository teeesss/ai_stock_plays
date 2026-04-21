# Gemini Memory Bridge - GIGACPO Terminal

## 🚀 Active Context: V23.60 (High-Density Cockpit Design Protocol)

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V23.60)**:
   - **High-Density Cockpit Layout**: Drastically reduced whitespace across all section headers, performance movers, and sector dossiers for a professional desktop aesthetic.
   - **Velocity Override (CSS Redesign)**: Character-based blocks replaced with a precision-CSS blue bar system (`#0ea5e9`).
   - **Strict Icon De-duplication**: `get_context_icon` now uses stateful pool tracking to ensure 100% variety across headlines and intelligence blocks.
   - **Redundant Label Filtering**: Automatic suppression of company names that are identical to their ticker symbols.
   - **Timezone Normalization**: Market session detection is normalized to **US/Eastern** time.
   - **Session Tagging Standards**: `PRE` (Orange), `LIVE` (Green + `L⚡`), `AH` (Red), `PM` (Light Blue).
   - **Horizontal Pulse Layout**: Sovereign Index Pulse uses a high-density 3-tile row layout for active sessions.
   - **Semiconductor Priority**: Weighted scoring (+75) for chip sector articles.
   - **Zero-Noise Protocol**: Enforced >0.1% volatility for inclusion; blacklisted "Dave Ramsey".

2. **AI UI Generation (V19.5)**:
   - AI/index.html is a GENERATED artifact. Source of truth is `AI/index_template.html`.
   - Use `python AI/engine/generate_ui.py` to rebuild UI. NEVER edit index.html directly.
   - Target Resolution: Columns Alpha/Risk/Hidden must be 60px.
   - Data Formatting: All metrics (mcap, performance, price) MUST show 1 decimal place minimum (e.g. 46.0T).
   - **Momentum Strip**: Using 7-day price action bars (Green=UP/FLAT, Red=DOWN). Secondary data fallback (openbb_supplement -> performance).
   - **Column Alignment**: The `#` column must be perfectly center-aligned with fixed 45px width and zero horizontal padding.

2. **Ticker Reconstruction (V10.3)**: 
   - NEVER use greedy regex for cashtags.
   - ALWAYS use `\b` word boundaries for ticker identification.
   - COLLAPSE fragments like `$ N V D A` but do NOT smashed into following words.

3. **AI Terminal UI Standards (V19.4)**:
   - **Column Sizing**: Alpha, Risk, and Hidden columns MUST be `60px` minimum.
   - **Data fallback**: P/E metrics must fallback to `forwardPE` or `trailingPE` if EPS trend is missing.
   - **Performance (1Y)**: 1y return data is fetched via `openbb_fetcher.py`.
   - **Consensus Wins**: Always prioritize OpenBB analyst consensus for "Upside" if available.
   - **Visual Premium**: Use `getScoreColor` logic for chips.
   
3. **Translation Turbine (V12.6)**: 
   - Concurrency: 16 workers (ThreadPoolExecutor).
   - Priority: `argostranslate` (Local) > `GoogleTranslator` (API).
   - Rules: No `[EN: Translation]` prefixes. Strip all formatting during flush.
   - Periodic Flush: Update JSON files every 100 posts to maintain live data.

3. **News Intelligence Anti-Spam (V18.2)**
   - `YAHOO_NEWS_MODULE.js` is automatically flattened and rebuilt by `sync_news.py`.
   - Strict `relatedTickers` or `clean_symbol` match required to bypass default Yahoo generic news.

4. **Forensic Recovery (V13.2)**: 
   - Use `engine/forensic_repair.py` if word-smashing reappears.
   - Whitelist of common words (Supply, They, Free) is used to de-ticker false positives.

5. **Stealth Session Path Hardening (V4.5)**:
   - ALWAYS ensure parent directories exist before Playwright `storage_state` calls.
   - Use absolute paths for `stealth_session.json` to prevent CWD-dependent `FileNotFoundError` when running from subdirectories (e.g., `AI/engine`).

6. **AI Watchlist Isolation (V19.2)**:
   - **Hardened Boundary**: ALL AI-specific logic, data, and tests are contained in `AI/`.
   - **Sync Orchestration**: Use `AI/engine/sync_ai_watchlist.py`. NEVER integrate AI tasks into root sync.
   - **Relativity**: All AI scripts must use relative pathing via `pathlib` for the `AI/` directory.
   - **Fierce Rule**: Modifying root CPO configuration from AI scripts is STRICTLY PROHIBITED.

### 🏛️ File Roles
- `engine/email_market_synopsis.py`: SIE Orchestrator. Manages NLP synthesis, price hydration, and responsive email dispatch.
- `engine/local_nlp.py`: Statistical NLP hub. Implements LSA (Sumy) and VADER for offline extractive summarization.
- `engine/yahoo_auth.py`: Centralized session/crumb manager with cache validation.
- `engine/live_prices.py`: High-stealth price extractor (10-ticker chunks).
- `engine/news_fetcher.py`: Stealth Yahoo News extraction with spam payload filtering.
- `engine/data_discovery.py`: Fundamentals & historical data discovery engine.
- `engine/openbb_fetcher.py`: Supplemental metrics (Analyst counts/Short interest).
- `engine/x_intel_deep_scraper.py`: Primary extraction + Live Reconstruction.
- `engine/sync_news.py`: Builds flat database/YAHOO_NEWS_MODULE.js asynchronously.
- `engine/translate_intel.py`: High-speed parallel translation.
- `engine/x_intel_instant_sync.py`: Manual sync override.
- `engine/x_intel_daily_sync.py`: Cron-scheduled staggered sync.
- `database/translation_cache.json`: Persistent memory of all translated posts.

### ⚠️ Known Quirks
- Nitter instances often fail under load; the scraper self-evicts bad nodes.
- Windows console requires `UTF-8` override to log CJK characters without crashing.
- `x_intel_master.json` must be rebuilt after every user sync.

[Handover Complete - 2026-04-21]
