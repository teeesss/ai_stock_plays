## 🚀 Active Context: V24.94 (Mobile UI & Logic Hardening)
[Status Synchronized - 2026-04-23]

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V24.7)**:
   - **Data-Driven Session Detection**: ALWAYS match session badges (AH, OVN, PRE) to the actual data source, not clock time. If OVN trades don't exist, scavenge AH data and label as `AH`.
   - **Session-Aware Delta Rendering**: Performance deltas MUST include the session label (e.g., `(AH +0.7%)`) to provide volatility context.
   - **24h Ghost Ticker Purge**: Database entries older than 24h must be purged during every save cycle to prevent stale data contamination.
   - **Sentiment Velocity Monitor (SVM)**: Real-time frequency tracking (4h vs 24h) to identify accelerating market narratives.
   - **Impersonation Rotation**: Multi-UA (Chrome/Edge/Safari) failover logic in `MacroAggregator` to bypass 401/403 data blocks.
   - **Institutional Anchor Pricing**: Standardized "C: $price" (previous close) injection for all non-standard session quotes.
   - **Dynamic Earnings Expansion**: Automatically increases intelligence list to 20 items and isolates earnings into high-visibility sections.
   - **Signal Decay Engine**: 5% hourly linear decay applied to macro catalysts.
   - **Stealth Fetching Protocol**: `curl_cffi` (Chrome146) + randomized jitter (3.3s-10s) + sequential domain queuing.
   - **Automated Verification**: `tests/test_temporal_integrity.py` ensures 100% accuracy in EST/Session detection.
   - **Sovereign Clock Architecture**: Anchors session classification (PRE/AH/OVN) to US/Eastern temporal ground truth.

2. **Dependency Guardian (V23.89)**:
   - **Auto-Restart Protocol**: Uses `os.execv` to automatically refresh the Python process after resolving missing dependencies.

3. **AI UI Generation (V19.5)**:
   - AI/index.html is a GENERATED artifact. Source of truth is `AI/index_template.html`.
   - Target Resolution: Columns Alpha/Risk/Hidden must be 60px.
   - Data Formatting: All metrics MUST show 1 decimal place minimum.

4. **Stealth Session Path Hardening (V4.5)**:
   - ALWAYS ensure parent directories exist before Playwright `storage_state` calls.
   - Use absolute paths for `stealth_session.json` to prevent CWD-dependent `FileNotFoundError`.

5. **Mobile Layout Hardening (V24.94)**:
   - **Responsive Typography**: Indices (26px), Crypto (24px), and Global (22px) font sizes boosted on mobile via media queries.
   - **Text Clipping Prevention**: Reduced column widths and eliminated `overflow: hidden` in Performance Movers and Watchlist to ensure all session badges and 'Close' prices are visible.
   - **Regex Isolation**: 'inject_price_flair' uses list-based word replacement with `\b` word boundaries and strict quote-stripping to prevent corruption of internal word characters (e.g., 'ON' in 'semiconductor').

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
