## 🚀 Active Context: V23.58 (Timezone-Aware Session Protocol)

### 🧩 Logic & Patterns
1. **Sovereign Intelligence Engine (V23.58)**:
   - **Timezone Normalization**: All market session detection logic in `email_market_synopsis.py` is normalized to **US/Eastern** time (standardizing VM/Server vs Local display).
   - **Session Tagging standards**:
     - `PRE`: Morning Market (4 AM - 9:30 AM EST) -> **Orange** (`#f59e0b`).
     - `LIVE`: Regular Market (9:30 AM - 4 PM EST) -> **Green** (`#10b981`) with specialized `L⚡` badge.
     - `AH`: After-Hours (4 PM - 8 PM EST) -> **Red** (`#ef4444`).
     - `PM`: Post-Market (Secondary Label) -> **Light Blue** (`#60a5fa`).
   - **Horizontal Pulse Layout**: Sovereign Index Pulse now uses a high-density horizontal row (3-tile) layout when indices are in `LIVE` or `AH` sessions. Desktop/Mobile views mirrored.
   - **Context-Aware News Icons**: Keywords map headlines to 12 distinct iconography themes (🛡️ Geopol, 🛢️ Energy, ⚖️ Macro, 🧠 AI, 📈 Earnings, 💻 Tech, 📜 Law, 🪙 Crypto, 🕵️ Scam, 💰 Wealth, 🚛 Logistics, 📡 Default).
   - **Intelligence Hardening**: Blacklisted `$CD` and "Dave Ramsey".
   - **Sparkline Decommissioning**: Removed sparkline rendering logic from all email components per user request.
   - **Suffix-Aware Session Detection**: `get_market_session` and `get_session_data` support global exchange suffixes (.DE, .HK, .ST, .AX).
   - **Mobile Optimization**: Centered Top Gainers/Losers via `display:block` stacking in `@media` CSS.
   - **Watchlist Column Hardening**: Ticker column `width="26%"` mandatory for international symbol support.
   - **High-Fidelity Pulse**: Expanded hydration to refresh all 113+ assets during active sessions.
   - **Branding Update**: Email title standardized to "Market Insights and Sovereign Intel". Decorative lightning bolts removed from header/subject.
   - **Zero-Noise Protocol**: `is_shite_ticker` neutralizes stablecoins and enforces >0.1% volatility for inclusion.
   - **Centralized Ticker Control**: Orchestration via CIFS-mounted `tickers.txt`.

1. **Pipeline Orchestration (V21.1)**:
   - **Unified Entry**: `PipelineOrchestrator` (`engine/pipeline_orchestrator.py`) manages full sync lifecycle for ALL endpoints (`/web/semi`, `/web/ai`).
   - **Lifecycle**: Live Prices + OBB Hydration → Orchestrator Build (Intelligence Engine + Field Mapping) → Deployment.

1. **Yahoo Stealth Protocol (V19.5)**:
   - **Decoupled Auth**: `engine/yahoo_auth.py` maintains a golden `auth_state.json`. 
   - **Stealth Rotation**: Uses Chrome 147.x User Agents + `chrome146` TLS Handshake (via `curl_cffi`).
   - **Velocity Jitter**: Randomized batch sizes (8-13 tickers) with 3.3s - 10.0s delays between bursts.

2. **Terminal UI Generation (V21.0)**:
   - Source of truth files: `web/semi/index_template.html` and `web/ai/index_template.html`.
   - Never edit output compiled `.html` files. Edit the template and then run the orchestrator.
   - **Column Sizing Target**: Alpha/Risk/Hidden columns MUST be `60px` minimum.

3. **Ticker Reconstruction (V10.3)**: 
   - NEVER use greedy regex for cashtags.
   - ALWAYS use `\b` word boundaries for ticker identification.
   - COLLAPSE fragments like `$ N V D A` but do NOT smash into following words.

### 🏛️ File Roles
- `engine/email_market_synopsis.py`: SIE Orchestrator. Manages NLP synthesis, price hydration, and responsive email dispatch.
- `engine/local_nlp.py`: Statistical NLP hub. Implements LSA (Sumy) and VADER for offline extractive summarization.
- `engine/pipeline_orchestrator.py`: Centralized conductors for multi-sector web terminal builds.
- `engine/yahoo_auth.py`: Centralized session/crumb manager with cache validation.
- `engine/live_prices.py`: High-stealth price extractor (10-ticker chunks).
- `engine/ticker_utils.py`: Single Source of Truth for ticker discovery and terminal mapping.

### ⚠️ Known Quirks
- **Responsive Media Queries**: Gmail often strips `<style>` blocks if they exceed size limits. Keep `@media` blocks concise.
- **NLP Sentiment**: VADER is rule-based; it may misinterpret complex irony or triple-negatives.
- **Nitter Resilience**: Instances often fail; self-eviction of bad nodes is active.

[Handover Complete - 2026-04-20]