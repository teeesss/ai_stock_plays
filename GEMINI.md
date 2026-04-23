### 🚀 Active Context: V25.0 (Intelligence Pipeline Ranking & Rotation)
[Status Synchronized - 2026-04-23]

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V25.0)**:
   - **Article Rotation Engine**: Deployed `sent_news_history.json` ledger to track previously sent URLs for 24h. The loop prefers fresh articles, dropping to stale ones ONLY if the quota falls short.
   - **Massive Rank Sifting**: Increased aggregator pool size to `200` to allow the engine to naturally degrade its threshold down the sorted list to guarantee 15 valid non-earnings items.
   - **Preserved Scoring Hierarchy**: NLP Engine correctly adds its VADER/Length bonuses directly ON TOP of the `MacroAggregator` score (e.g., +30 for macro, +20 for tech), preserving original ranking priorities.
   - **Unified Mirror UI**: Sovereign Index Pulse and Crypto tiles structurally mirror the Global Markets design. 
   - **JIT Global Data Hardening**: Explicitly force-fetches global indices (`^HSI`, `^N225`, `^GDAXI`, `^FTSE`) during the price-refresh cycle.
   - **Desktop Density Scaling**: Applied a global +20% font-size increase for desktop viewports (600px+).
   - **100% Dual-Surface Architecture**: Distinct `<div class="desktop-only">` and `<div class="mobile-only">` wrappers.
   - **3-Column Mobile Pulse**: Pulse sections (Index/Crypto) maintain 3-column density on mobile.
   - **Data-Driven Session Detection**: ALWAYS match session badges (AH, OVN, PRE) to the actual data source, not clock time.
   - **24h Ghost Ticker Purge**: Database entries older than 24h must be purged during every save cycle.
   - **Signal Decay Engine**: 5% hourly linear decay applied to macro catalysts.

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
