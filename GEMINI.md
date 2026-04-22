## 🚀 Active Context: V24.2 (Hardened Intelligence & News Velocity)

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V24.2)**:
   - **Sentiment Velocity Monitor (SVM)**: Real-time frequency tracking (4h vs 24h) to identify accelerating market narratives.
   - **Impersonation Rotation**: Multi-UA (Chrome/Edge/Safari) failover logic in `MacroAggregator` to bypass 401/403 data blocks.
   - **Institutional Anchor Pricing**: Standardized "C: $price" (previous close) injection for all non-standard session quotes.
   - **Dynamic Earnings Expansion**: Automatically increases intelligence list to 20 items and isolates earnings into high-visibility sections.
   - **Signal Decay Engine**: 5% hourly linear decay applied to macro catalysts to ensure maximum thematic freshness.
   - **JIT Narrative Synthesis**: Scrapes real-time institutional recaps to anchor executive summaries.
   - **Stealth Fetching Protocol**: `curl_cffi` (Chrome146) + randomized jitter (3.3s-10s) + sequential domain queuing.
   - **Automated Verification**: `tests/test_temporal_integrity.py` ensures 100% accuracy in EST/Session detection.
   - **Sovereign Clock Architecture**: Anchors session classification (PRE/AH/OVN) to US/Eastern temporal ground truth.
   - **Gmail Clipping Defense**: Automated HTML minification ensuring payloads remain < 102KB.

2. **Dependency Guardian (V23.89)**:
   - **Auto-Restart Protocol**: Uses `os.execv` to automatically refresh the Python process after resolving missing dependencies, ensuring zero-interruption execution.

3. **AI UI Generation (V19.5)**:
   - AI/index.html is a GENERATED artifact. Source of truth is `AI/index_template.html`.
   - Target Resolution: Columns Alpha/Risk/Hidden must be 60px.
   - Data Formatting: All metrics (mcap, performance, price) MUST show 1 decimal place minimum (e.g. 46.0T).

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

[Status Synchronized - 2026-04-22]
