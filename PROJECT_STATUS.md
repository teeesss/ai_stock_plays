# Project Status — April 20, 2026
## 🚀 Version: V22.96 (Granular 15-Minute Protocol)

Status: **PRODUCTION HARDENED — DECOUPLED & GRANULAR**

📊 **Project Status: Sovereign Intel**
- **Current Tier**: V22.96 (Granular Lock) / V22.94 (High-Fidelity OVN)
- **Critical Progress**: Successfully decoupled the static terminal universe from the dynamic news-driven discovery engine. Implemented a per-ticker TTL lock that ensures no asset is re-synced within 15 minutes, regardless of which script (Manual, Sync, or Email) initiates the fetch. Transitioned from a global file-level cache to a high-precision asset-level cache.
- **Next Milestone**: Automated cron-trigger sequencing for market opens.

Date: 2026-04-20
Tests: **55 passing / 0 failing**

---

### V22.96 — Granular 15-Minute Protocol
- **Granular Lock**: Hardened `live_prices.py` to check TTL at the ticker level. Assets are now only re-fetched if their specific timestamp in the price database is > 15m old.
- **Email Hardening & Branding**: Implemented global link neutralization (zero-width spaces) to kill URL creep. Set sender name to "Market News".
- **Universe Decoupling**: Reverted global unification. `live_prices.py` now specifically tracks only the **Static Terminal Universe** (Root + AI), while `email_market_synopsis.py` handles its own **Dynamic Discovery**.
- Date: 2026-04-20

---

### V22.94 — High-Fidelity Overnight (BOATS)
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

### V21.2 — Triple-Layer Unified Sync
- **Unified Conductor**: Created `engine/sync_triple.py` to coordinate Tweets, News, and OCR into a single transactional pass. 
- **OCR Controls**: Added `--skip-ocr` functionality to allow rapid 60-second "News & Post" updates without chart analysis delay.
- **Workflow Mastery**: Generated `docs/SYNC_GUIDE.md` as the definitive SOP for terminal operations.
- Date: 2026-04-18

---

### V21.1 — Sector Independence & Data Continuity
- **AI Ticker Hydration**: Fixed missing Analyst/Short/Performance data on AI terminal. `engine/openbb_fetcher.py` now recursively hydrates all terminal variants.
- **Research Key Translation**: Added legacy key backward-compatibility mapping to `PipelineOrchestrator`.
- Date: 2026-04-18

---

### V21.0 — Modular Pipeline & High Density Web endpoints
- **Structural Mastery**: Decoupled core logic from web endpoints. /web/semi and /web/ai now isolated.
- **Unified Orchestration**: Global `PipelineOrchestrator` handles 100% of data-to-UI processing.
- Date: 2026-04-18

---

### V20.0 — Unified Pipeline Orchestration (2026-04-18)
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
