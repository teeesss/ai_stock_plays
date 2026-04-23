### 🚀 Active Context: V24.98 (100% Desktop/Mobile View Separation)
[Status Synchronized - 2026-04-23]

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V24.98)**:
   - **100% Dual-Surface Architecture**: Introduced distinct `<div class="desktop-only">` and `<div class="mobile-only">` wrappers in `email_market_synopsis.py` to eliminate responsive CSS constraints. Desktop view maintains horizontal side-by-side components (Indices, Global Markets, Movers), while mobile view strictly enforces vertical stacking and density limits.
   - **3-Column Mobile Pulse**: Pulse sections (Index/Crypto) maintain 3-column density on mobile via adaptive font scaling (22px values for 375px, 18px for 320px).
   - **Vertical Movers Stack**: "Session Performance Movers" lock to a single-column vertical stack on mobile to prevent horizontal clipping.
   - **Watchlist Density**: Adjusted column ratios (25%/75%) and reduced font sizes to ensure single-line data integrity on narrow screens.
   - **Ticker Flair Integrity**: Implemented positional reconstruction in `inject_price_flair` to prevent word-internal corruption (e.g., 'ON' inside 'semiconductor').
   - **Data-Driven Session Detection**: ALWAYS match session badges (AH, OVN, PRE) to the actual data source, not clock time.
   - **Session-Aware Delta Rendering**: Performance deltas MUST include the session label (e.g., `(AH +0.7%)`) to provide volatility context.
   - **24h Ghost Ticker Purge**: Database entries older than 24h must be purged during every save cycle to prevent stale data contamination.
   - **Sentiment Velocity Monitor (SVM)**: Real-time frequency tracking (4h vs 24h) to identify accelerating market narratives.
   - **Impersonation Rotation**: Multi-UA (Chrome/Edge/Safari) failover logic in `MacroAggregator` to bypass 401/403 data blocks.
   - **Institutional Anchor Pricing**: Standardized "C: $price" (previous close) injection for all non-standard session quotes.
   - **Dynamic Earnings Expansion**: Automatically increases intelligence list to 20 items and isolates earnings into high-visibility sections.
   - **Signal Decay Engine**: 5% hourly linear decay applied to macro catalysts.
   - **Stealth Fetching Protocol**: `curl_cffi` (Chrome146) + randomized jitter (3.3s-10s) + sequential domain queuing.

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
