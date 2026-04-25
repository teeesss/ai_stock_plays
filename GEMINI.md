### 🚀 Active Context: V28 (Config-First & FinVADER NLP Architecture)
[Status Synchronized - 2026-04-25]

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V26.0)**:
   - **Extreme Payload Optimization**: HTML payload must remain under 102KB. ACHIEVED: 63KB (42% reduction) by transitioning from inline styles to a centralized <style> block in the <head>.
   - **Centralized CSS Architecture**: Use predefined CSS classes (.pulse-card, .news-item, .watchlist-row) instead of repeated inline style attributes.
   - **Institutional Source Hardening**: strictly blacklist low-signal sources (e.g., "The Motley Fool"). Normalize source badges by removing "GOOG/" prefixes for professional clarity.
   - **Article Rotation Engine**: Deployed sent_news_history.json ledger to track previously sent URLs for 24h. The loop prefers fresh articles.
   - **Massive Rank Sifting**: Increased aggregator pool size to 200 to allow the engine to naturally degrade its threshold down the sorted list to guarantee 15 valid non-earnings items.
   - **Preserved Scoring Hierarchy**: NLP Engine adds bonuses (+30 macro, +20 tech) directly ON TOP of MacroAggregator scores.
   - **Unified Mirror UI**: Sovereign Index Pulse and Crypto tiles structurally mirror the Global Markets design. 
   - **JIT Global Data Hardening**: Explicitly force-fetches global indices (^HSI, ^N225, ^GDAXI, ^FTSE) during the price-refresh cycle.
   - **Desktop Density Scaling**: Applied a global +20% font-size increase for desktop viewports (600px+).
   - **Data-Driven Session Detection**: ALWAYS match session badges (AH, OVN, PRE) to the actual data source, not clock time.
   - **24h Ghost Ticker Purge**: Database entries older than 24h must be purged during every save cycle.
   - **Sovereign Resilience Engine (V26.6)**: 
       - **Multi-Tier Rescue**: Use a 5-gateway pool (vx_rescue_fetcher.py) with OpenGraph HTML scraping as a secondary fallback to bypass API rate limits.
       - **Adaptive Health Monitor**: Demote and blacklist 429-saturated gateways for 10 minutes.
       - **Identity 160**: Standardize all scraper/rescue identities on Chrome 160.0.8827 (2026-grade).
   - **Sovereign Layout Hardening (V26.7)**:
       - **Single-Line Mandate**: EVERY ticker row must be wrapped in .u-nowrap with white-space: nowrap !important. 
       - **Zero Break Policy**: Explicit <br/> tags are strictly forbidden inside ticker data cells. Use pipes | or mid-dots • for density.
       - **Session Badging**: Use Bold Orange C (Closed) and Bold Green L (Live) for instant session recognition.
       - **Automated QA**: Run tests/test_layout_integrity.py after any UI/CSS change to prevent regressions.
   - **Automated Verification Hardening (V26.8)**:
       - **Always-Run Mandate**: Mandatory test execution via run_all_tests.py injected into start.bat (Full Refresh). 
       - **Path Integrity**: All tests must target /web/semi/ or /web/ai/ for template inspection. Root HTML inspection is deprecated.
       - **Session Labeling**: Use single-quoted 'AH' and 'PM' in live_prices.py to maintain compatibility with legacy test assertions.
       - **Source Check Priority**: postMarketPrice must be requested before preMarketPrice in API field strings to satisfy priority logic tests.
       - **Decoupled Pricing Math**: Always render close_price (labeled 'C') and ext_price (labeled 'AH/PM') separately in mover lists. Never allow the extended price to clobber the closing price in the primary display slot.
    - **News Aesthetic Mandate (V26.9)**:
        - **Alternating Tile Backgrounds**: News rows must use high-contrast alternating backgrounds (Subtle Blue: rgba(56,189,248,0.07) / Subtle Green: rgba(74,222,128,0.07)) with matching borders and tinted text colors.
        - **Source De-duplication**: Headlines must be stripped of redundant source names. Institutional badges must have TLDs stripped (e.g., BLOOMBERG.COM -> BLOOMBERG).
    - **Temporal Hierarchy Mandate (V26.14)**:
        - **Hierarchy Leader**: engine/market_session.py is the absolute authority for session/calendar logic.
        - **Zero Duplication Policy**: No script may calculate weekday() or hour() for market-gating. Defer to MarketSession.
         - **Weekend Stasis Gate**: All data-fetch pipelines MUST call is_market_stasis() to prevent "Zombie Fetches" on Sat/Sun.
     - **Config-First Scoring Architecture (V27/V28)**:
         - **YAML Single Source of Truth**: ALL scoring weights, keywords, feeds, tickers, and bonus terms live in `config/macro_config.yaml`. NEVER hardcode scoring data in Python source.
         - **FinVADER Sentiment Injection**: The NLP engine (`local_nlp.py`) dynamically pulls the Loughran-McDonald financial dictionary into its VADER instance.
         - **YAML Lexicon Overrides**: You can mathematically dictate sentiment bounds (e.g. `breakthrough: 2.5`) inside the `vader_financial_lexicon` block of the YAML file.
         - **Global Relevance Floor**: Articles scoring below 15.0 are instantly vaporized by the NLP engine. This prevents the Rotation Engine from starving out and filling its quota with garbage news on weekends.
         - **Bonus Keywords**: Variable-point high-signal terms (CPO: 120, SILICON PHOTONICS: 130, etc.) grant extra points ON TOP of the standard +50 from priority_keywords.
         - **Cluster Multiplier**: Headlines with 2+ high-signal terms (CPO + NVIDIA, HBM + BLACKWELL) receive a 1.55x score multiplier.
         - **Billion-Scale Detection**: Configurable Regex detects $160B / 50 billion / 100BN figures and grants +45 bonus.
         - **Institutional Hierarchy**: 45+ Bulge Bracket, Boutique, Hedge Fund, and PE firm names carry +50 weight each.
         - **Robust Fallback**: Engine uses hardcoded defaults if YAML is missing or corrupted.

2. **Dependency Guardian (V23.89)**:
   - **Auto-Restart Protocol**: Uses os.execv to automatically refresh the Python process after resolving missing dependencies.

3. **AI UI Generation (V19.5)**:
   - AI/index.html is a GENERATED artifact. Source of truth is AI/index_template.html.

4. **Stealth Session Path Hardening (V4.5)**:
   - ALWAYS ensure parent directories exist before Playwright storage_state calls.
   - Use absolute paths for stealth_session.json to prevent CWD-dependent FileNotFoundError.

### 🏛️ File Roles
- `config/macro_config.yaml`: **V28 Single Source of Truth**. All scoring weights, lexicons, feeds, and multipliers. Edit this file to tune intelligence priorities — NEVER edit Python source for scoring changes.
- `engine/email_market_synopsis.py`: SIE Orchestrator. Managed high-density "Cockpit" UI and minified HTML dispatch.
- `engine/macro_aggregator.py`: Config-driven multi-source news aggregator with weighted scoring, cluster bonuses, and billion-scale detection.
- `engine/dependency_mgr.py`: Cross-platform dependency resolver with auto-restart (os.execv) logic.
- `engine/local_nlp.py`: Statistical NLP hub (LSA, VADER, TF-IDF).
- `engine/yahoo_auth.py`: Centralized stealth session/crumb manager.
- `engine/market_session.py`: Hierarchy Leader. Central authority for market calendar and session temporal logic.
- `engine/live_prices.py`: High-stealth price extractor (10-ticker chunks).

### ⚠️ Known Quirks
- Gmail will clip messages if the minification fails or if CSS classes exceed length limits.
- os.execv behaves differently on Windows than Linux/Unix (replaces process image).
