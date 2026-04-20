## 🚀 Active Context: V22.96 (Granular 15-Minute Protocol)

### 🧩 Logic & Patterns
0. **Sovereign Intelligence Engine (V22.96)**:
   - **Granular 15-Minute Lock**: Hardened 900s cache window enforced at the **Ticker Level**. Individual assets are skipped if their specific `live_prices.json` timestamp is fresh (< 15m old).
   - **Universe Decoupling**: Reverted global unification and narrowed `live_prices.py` to only track **Static Terminals** (Root/AI). `email_market_synopsis.py` handles **Dynamic Discovery** independently.
   - **BOATS Overnight Integration (V22.94)**: Uses `&overnightPrice=true` to capture Blue Ocean ATS data. Mapping: `overnightMarketPrice` → `OVN` tag.
   - **Session-Aware Labeling**: Integrated `PM` (Pre), `AH` (After), and `OVN` (Overnight). Prioritization: `OVN` > `PRE` > `POST`.
   - **Cross-Section Diversification**: Alpha and Momentum terminal strips MUST be unique. Momentum = Volume Force; Alpha = Top Price Movers (excluding Momentum pool).
   - **No-URL Protocol**: Terminal strips (Alpha/Momentum) are strictly non-interactive `<span>` labels. Hyperlinks are reserved for Discovery sections.
   - **NLP Synthesis**: `engine/local_nlp.py` uses Sumy (LSA) and VADER (Sentiment) for 100% offline extractive summarization.

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