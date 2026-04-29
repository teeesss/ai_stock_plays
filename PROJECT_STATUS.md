# Project Status: Market Intelligence Engine

## 🚀 Current Milestone: V28.8 (Sovereign Intelligence Hardening)
**Status**: 🟢 PRODUCTION-DEPLOYED // **Aesthetic**: Institutional Alternate Tiles // **Logic**: Dual-Dispatch (Email + Web)
---
### 🧩 Core Accomplishments
- **[NEW] Web Synopsis Endpoint (V28.8)**: Integrated automatic deployment of the market intelligence dossier to `bmwseals.com/email`. Every email dispatch now simultaneously updates the web view.
- **[NEW] Documentation Synchronization (V28.8)**: Achieved total parity across `.cursorrules`, `GEMINI.md`, and `CLAUDE.md`. Established the "Mirror Mandate" to ensure rules remain consistent across all agents.
- **[NEW] Mandatory Hierarchical Architecture (V28.71)**: Rebuilt the entire intelligence pipeline to follow a strict hierarchy-leader pattern. Logging is now initialized at the absolute top of all main scripts. Verified 100% visibility across Scraper, Price Sync, and Brain Update.

## 🚀 Version: V28.8 (Sovereign Intelligence Hardening)
Status: **PRODUCTION DEPLOYED — HARDENED**

📊 **Project Status: Sovereign Intel**
- **Current Tier**: V28.8 (Web Deployment & Sync Parity)
- **Critical Progress**: Hardened Sovereign Intelligence Engine (V28.8) by enabling dual-dispatch (Email + Web). Synchronized documentation across all rules files (`.cursorrules`, `GEMINI.md`, `CLAUDE.md`) to maintain architectural integrity.
- **Next Milestone**: Monitor web endpoint traffic and ensure `RemoteSync` handles intermittent SFTP connectivity gracefully.

Date: 2026-04-29
Tests: **158 passing / 0 failing ✅ FULLY RESTORED**


---

### 🚀 Previous Status: V28 — Subscription-Free & Relevance Hardening
- [x] **Subscription-Free Hardening**: 100% block on Bloomberg, WSJ, Seeking Alpha, and Barron's.
- [x] **Geographic Relevance Gate**: Integrated Tech-Anchor relevance gate to prioritize NASDAQ/S&P 500 alpha.
- Date: 2026-04-24

---

### 🚀 Previous Status: V28 — Environment Hardening // Auto-Guardian
- [x] **Auto-Dependency Guardian (V28)**: All core scripts now auto-check for missing libraries (bs4, playwright, etc.) and offer one-click installation. Supports Windows & Linux.
- [x] **Timezone-Aware Session Logic (V28)**: Implemented `_get_est_now()` to normalize VM/Server calculations to US/Eastern (EDT). Resolves CST vs EST session misclassification.
- [x] **PM Blue Lightening (V28)**: Refined `PM` session badge color to `#60a5fa` for better visual harmony.
- [x] **LIVE (L⚡) Badge refined (V28)**: Integrated the lightning bolt icon into the high-alpha green regular session badge.
- **Stability Fixes**: Resolved `NameError` (log) and `TypeError` in sidecar trigger logic.
- Date: 2026-04-20

---

### [V28] — 2026-04-21: Environment Hardening (Auto-Guardian)
- [x] **Auto-Dependency Guardian**: Integrated `dependency_mgr.py` into all core scripts. Detects missing libs (bs4, playwright, curl-cffi, etc.) and offers interactive installation.
- [x] **Cross-Platform Compatibility**: Guardian supports both Windows and Linux, utilizing `sys.executable` for precision pip targeting.
- [x] **Timezone Parity (V28)**: Normalized market session detection to US/Eastern (EST).
- [x] **UI Polish**: Lightened PM Blue (#60a5fa) and added `L⚡` badge to LIVE sessions.

---

### V23.48 — Visual Supercycle
- **Context-Aware News Intelligence**: Replaced generic news markers with a dynamic icon system (📡, 🛡️, ⚖️, 🧠, 📈). Headlines are analyzed for geopolitical, energy, macro, and AI keywords.
- **Isolated Sparkline Sidecar**: Created `engine/email_spark_fetcher.py`. This sidecar fetches 1-day regular session chart data and renders lightweight SVG sparklines directly in the watchlist.
- **UI Hardening**: Increased watchlist ticker column width to **26%** to accommodate international suffixes. logic now automatically hides "Futures" during active trading.
- **Watchlist Cleanliness**: Purged custom stock "Notes" from watchlist items to maintain a high-fidelity look.
- Date: 2026-04-20

---

### V23.47 — Sovereign Session Intelligence
- **Suffix-Aware Session Tracking**: Refactored `get_market_session` to support global exchange suffixes (.DE, .HK, .ST, .AX). Mapped international symbols to local trading hours (in EST).
- **Green `L⚡` Badge**: Deployed a specialized high-visibility badge for active market sessions.
- **Stability Fixes**: Resolved `NameError` (log) and `TypeError` in sidecar trigger logic.
- Date: 2026-04-20

---

### V23.45 — Session Parity Hardening
- **Session Parity Hardening**: Resolved a session stasis defect in `live_prices.py` where assets would remain tagged as `OVN` despite pre-market trading activity. Prioritized `PRE/POST` fields over the Yahoo `marketState` property.
- **Hybrid Session Locking**: Hardened `get_session_data` fallback. Engine now holds `OVN` price data when entering the `PM` session window if fresh Pre-Market trades are absent, preventing overnight gain erasure.
- **Badge UI & Price Injection**: Restored current Price ($) and % Change to all Watchlist and Sector Dossier rows. Introduced HSL-colored session badges (OVN/PM/AH).
- **Ubuntu Pulse Deployment**: Finalized the automated dispatch pipeline. `email.sh` on Ubuntu VM now targets a CIFS-mounted `tickers.txt` on the Windows host for live watchlist updates.
- Date: 2026-04-20

---

### V28 — Granular 15-Minute Protocol
- **Granular Lock**: Hardened `live_prices.py` to check TTL at the ticker level. Assets are now only re-fetched if their specific timestamp in the price database is > 15m old.
- **Email Hardening & Branding**: Implemented global link neutralization (zero-width spaces) to kill URL creep. Set sender name to "Market News".
- **Universe Decoupling**: Reverted global unification. `live_prices.py` now specifically tracks only the **Static Terminal Universe** (Root + AI), while `email_market_synopsis.py` handles its own **Dynamic Discovery**.
- Date: 2026-04-20

---

### V28 — High-Fidelity Overnight (BOATS)
- **BOATS Integration**: Unlocked Blue Ocean ATS (BOATS) overnight trading data by integrating the `overnightPrice=true` API parameter.
- **Session Labeling**: Integrated `PM`, `AH`, and `OVN` tags to provide real-time session awareness on the terminal.
- Date: 2026-04-19

---

### V22.0 — Local NLP Intelligence & Autonomous Dossiers
- **NLP Synthesis**: Integrated `engine/local_nlp.py` using Sumy (LSA Summarization), VADER (Sentiment), and TF-IDF (Key Themes).
- **Dossier Refinement**: Rewrote `email_market_synopsis.py` to support 80% distinct Market vs. Sector streams.
- **Macro Hydration**: Fixed missing prices/percentages for index futures ($NQ, $ES, $YM) and crypto ($BTC, $ETH).
- Date: 2026-04-19

---

### V28 — Triple-Layer Unified Sync
- **Unified Conductor**: Created `engine/sync_triple.py` to coordinate Tweets, News, and OCR into a single transactional pass.
- **OCR Controls**: Added `--skip-ocr` functionality to allow rapid 60-second "News & Post" updates without chart analysis delay.
- **Workflow Mastery**: Generated `docs/SYNC_GUIDE.md` as the definitive SOP for terminal operations.
- Date: 2026-04-18

---

### V28 — Sector Independence & Data Continuity
- **AI Ticker Hydration**: Fixed missing Analyst/Short/Performance data on AI terminal. `engine/openbb_fetcher.py` now recursively hydrates all terminal variants.
- **Research Key Translation**: Added legacy key backward-compatibility mapping to `PipelineOrchestrator`.
- Date: 2026-04-18

---

### V28 — Modular Pipeline & High Density Web endpoints
- **Structural Mastery**: Decoupled core logic from web endpoints. /web/semi and /web/ai now isolated.
- **Unified Orchestration**: Global `PipelineOrchestrator` handles 100% of data-to-UI processing.
- Date: 2026-04-18

---

### V28 — Unified Pipeline Orchestration (2026-04-18)
- **Global Orchestrator**: Unified full system sync including `VisualBuzzAggregator` and `sync_news` into a single entry point (`engine/global_orchestrator.py`).
- **Dynamic Research**: `PipelineOrchestrator` now sources live financials and consensus upside from `CPO_MASTER_DATA.json`.
- Date: 2026-04-18

---

### Known Rules (Lessons Learned)
- `passesFilters()` P/E sentinel: **999 = no EPS data**. Max filter active → exclude 999. Min-only → allow.
- OBB fields: always use null-safe `?.` access before calling sfloat().
- Buzz counts are **integers**, not floats. Always use `parseInt(val, 10)`.
- Never define the same function name twice in `cpo_plays.html`.
- Dashboard data is minified JSON on a single line — edits must be surgical via engine scripts, not manual.

[GIGACPO V7.0 Production Snapshot — 2026-04-14]
