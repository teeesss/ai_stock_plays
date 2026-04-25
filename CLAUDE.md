### 🚀 Active Context: V28 (Config-First & Weekend-Aware Intelligence)
[Status Synchronized - 2026-04-25]

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V26.0)**:
   - **Extreme Payload Optimization**: HTML payload must remain under 102KB. ACHIEVED: 63KB (42% reduction) by transitioning from inline styles to a centralized `<style>` block in the `<head>`.
   - **Centralized CSS Architecture**: Use predefined CSS classes (`.pulse-card`, `.news-item`, `.watchlist-row`) instead of repeated inline `style` attributes.
   - **Institutional Source Hardening**: strictly blacklist low-signal sources (e.g., "The Motley Fool"). Normalize source badges by removing "GOOG/" prefixes for professional clarity.
   - **Article Rotation Engine**: Deployed `sent_news_history.json` ledger to track previously sent URLs for 24h. The loop prefers fresh articles.
   - **Massive Rank Sifting**: Increased aggregator pool size to `200` to allow the engine to naturally degrade its threshold down the sorted list to guarantee 15 valid non-earnings items.
   - **Preserved Scoring Hierarchy**: NLP Engine adds bonuses (+30 macro, +20 tech) directly ON TOP of `MacroAggregator` scores.
   - **Unified Mirror UI**: Sovereign Index Pulse and Crypto tiles structurally mirror the Global Markets design. 
   - **JIT Global Data Hardening**: Explicitly force-fetches global indices (`^HSI`, `^N225`, `^GDAXI`, `^FTSE`) during the price-refresh cycle.
   - **Desktop Density Scaling**: Applied a global +20% font-size increase for desktop viewports (600px+).
   - **Data-Driven Session Detection**: ALWAYS match session badges (AH, OVN, PRE) to the actual data source, not clock time.
   - **24h Ghost Ticker Purge**: Database entries older than 24h must be purged during every save cycle.
   - **Sovereign Resilience Engine (V26.6)**: 
       - **Multi-Tier Rescue**: Use a 5-gateway pool (`vx_rescue_fetcher.py`) with OpenGraph HTML scraping as a secondary fallback to bypass API rate limits.
       - **Adaptive Health Monitor**: Demote and blacklist 429-saturated gateways for 10 minutes.
       - **Identity 160**: Standardize all scraper/rescue identities on **Chrome 160.0.8827** (2026-grade).
    - **Sovereign Layout Hardening (V26.7)**:
        - **Single-Line Mandate**: EVERY ticker row must be wrapped in `.u-nowrap` with `white-space: nowrap !important`. 
    - **Automated Verification Hardening (V26.8)**:
        - **Always-Run Mandate**: Mandatory test execution via `run_all_tests.py` injected into `start.bat`. 
        - **Decoupled Pricing Math**: Always render `close_price` (labeled 'C') and `ext_price` (labeled 'AH/PM') separately in mover lists.
    - **News Aesthetic Mandate (V26.9)**:
        - **Alternating Tile Backgrounds**: News rows must use high-contrast alternating backgrounds.
        - **Source De-duplication**: Headlines must be stripped of redundant source names.
    - **Sovereign Intelligence Hardening (V28)**:
        - **Weekend Freshness**: Lookback window expands to **60h** during Sat/Sun stasis via `MarketSession`.
        - **Double-Enrichment Fix**: Aggregator returns plain text; flair is injected ONLY once in the email script.
        - **Case-Insensitive Badges**: All `source_space_map` lookups are case-normalized.
        - **Ticker Blacklist**: 'FORM' is strictly blacklisted to prevent common-word collisions.

2. **Dependency Guardian (V23.89)**:
   - **Auto-Restart Protocol**: Uses `os.execv` to automatically refresh the Python process after resolving missing dependencies.

3. **AI UI Generation (V19.5)**:
   - AI/index.html is a GENERATED artifact. Source of truth is `AI/index_template.html`.

4. **Stealth Session Path Hardening (V4.5)**:
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
