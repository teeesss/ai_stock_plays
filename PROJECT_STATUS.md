# Project Status — April 19, 2026
## 🚀 Version: V20.0 (Unified Pipeline & Production Mastery)

Status: **PRODUCTION DEPLOYED — SI-PH NEWS ACTIVATED**
Date: 2026-04-17
Tests: **52 passing / 0 failing**

---

### V20.0 — Unified Pipeline Orchestration (2026-04-18)
- **Global Orchestrator**: Unified full system sync including `VisualBuzzAggregator` and `sync_news` into a single entry point (`engine/global_orchestrator.py`).
- **Dynamic Research**: `PipelineOrchestrator` now sources live financials and consensus upside from `CPO_MASTER_DATA.json` instead of placeholders.
- **Scoring Engine**: Verified Alpha/Risk/Hidden scoring logic across 29 tickers with dynamic percentile normalization.
- **Deprecation**: Cleaned up legacy `rebuild_master.py` scripts to point exclusively to the modular pipeline.
- **QA**: 100% pass on refactored `tests/test_intelligence_engine.py`.

### V19.6 — Intelligence Engine V2.0 Modular (2026-04-18)

### V19.5 — AI Terminal UX Refinement (2025-04-18)
- **AI Terminal**: Consistently consolidated Ticker + Company + Momentum into a single column.
- **AI Terminal**: Implemented Case-Insensitive filtering (toUpperCase) for Sectors and Exchanges.
- **AI Terminal**: Hardened `LIVE_PRICES` data binding to fix "Day $" and "% Chg" display issues.
- **Sync**: Automated SFTP upload enabled for both root and AI `live_prices.py` scripts.
- **Refactor**: Intelligence Engine V2.0 Modularized into `engine/` for cross-terminal reuse.
- **Testing**: Regression suite `test_modular_engine.py` verified 100% pass on Alpha floor logic.

### V17.1 — Hardened Sync & Performance Bridge (2026-04-17)
- **Hardened Deployment**: Transitioned to root-flattened SFTP architecture on `bmwseals.com` to prevent relative-path 404 errors.
- **Performance Virtualization**: Implemented 50-itemNews pagination and deferred hydration to maintain 60FPS dashboard scrolling with 6,900 articles.
- **Data Universe**: Hydrated News DB covering 113+ monitoried tickers with 7-day lookback logic.
- **Anti-Spam Filter**: Implemented strict ticker text-matching to reject default Yahoo noise; purged 751 spam articles.
- **UI visibility**: Corrected CSS icon clipping for 📰 newspaper triggers.

---

### V16.0 — Institutional Alpha & Glass Supercycle (2026-04-16)

Three silent bugs were discovered and fixed in `cpo_plays.html → passesFilters()`:

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| **Duplicate functions** | `filterIntel()`, `openIntelModal()`, `renderBuzz()` defined twice — second stub silently won | Removed stale first definitions |
| **P/E Sentinel (999)** | `e.pe26 < maxPe26` incorrectly blocked stocks with no EPS data when any max filter was active | Added `pe26Active` check + 999 sentinel guard |
| **OBB Null Crash** | `e.obb.inst_ownership_pct` crashed if `obb` was null/missing | Added null-safe `?.` access + `hasInst/Short/Analysts` guards |
| **Buzz parseInt** | `sfloat(e.buzz?.['7d'])` misread integer buzz counts | Changed to `parseInt(..., 10)` |

**QA**: `tests/test_dashboard_filters.py` added with 29 new tests across 4 classes.
Full suite: **50 tests, 100% passing.**

---

### V15.0 — Surgical Repair & Dependency Hardening (2026-04-14)
- **V11.0 Surgical Ticker Repair**: Boundary-aware regex to collapse fragmented tickers.
- **Dependency Hardening**: Centralized `requirements.txt`. Synchronized `bs4`, `playwright-stealth`, `curl_cffi`, `deep_translator`.
- [x] **Task 2: Expanded X Search Filtering** — Added Username select and Date From/To inputs to dashboard; updated `x_intel_deep_scraper.py` with CLI flags (`--since`, `--until`, `--query`).
- [x] **Task 3: Username Management Script** — Created `engine/manage_users.py` and `database/monitored_users.json` for dynamic user tracking.
- [x] **Task 4: BetterTwitFix Integration** — Implemented `engine/vx_rescue_fetcher.py` and integrated into scraper as a fallback repair layer for truncated/broken tweets.
- [x] **Task 5: Image Intelligence Hardening** — Removed OCR batch limits in `image_analyzer.py`; modernized `visual_buzz_aggregator.py` to handle all monitored users dynamically.
- [x] **Task 6: Unified Terminal** — Created `terminal.py` menu system for orchestrating all 11 engine scripts.
- [x] **Task 13F: Institutional Alpha** — Created `engine/inst_13f_fetcher.py` to pull 13F hedge fund positioning (WhaleRock, Altimeter, Coatue) into master data.
- [x] **Task LIDE: Glass Supercycle Mapping** — Created `engine/glass_intel_mapper.py` to map the LIDE/TGV supply chain (LPKF, Absolics, Corning) into the terminal.
- [x] **Task AI: Alpha Intelligence Engine** — Created `AI/engine/rebuild_master.py` with dynamic percentile scoring formula + case-insensitive filter normalization.
- [x] **Task AI: Live Price Autopilot** — Updated `live_prices.py` (Both) to auto-upload to SFTP.
- **Test Suite**: 50 tests across ticker reconstruction, filter logic, audit, and ticker repair.
- **Top Alpha Plays**: $ASMVY (ASMPT), $SIVE (Sivers), $AJINY (Ajinomoto), $LPK.DE (LPKF), $COHR (Coherent), $LITE (Lumentum), $CRDO (Credo).
- **Stealth Strategy**: Ghost-Mode V2.8 (Playwright + curl-cffi) active.

### Known Rules (Lessons Learned)
- `passesFilters()` P/E sentinel: **999 = no EPS data**. Max filter active → exclude 999. Min-only → allow.
- OBB fields: always use null-safe `?.` access before calling sfloat(). Many watchlist stocks have no OBB data.
- Buzz counts are **integers**, not floats. Always use `parseInt(val, 10)`.
- Never define the same function name twice in `cpo_plays.html` — JS silently overwrites with the last definition.
- Dashboard data is minified JSON on a single line — edits must be surgical via engine scripts, not manual.

[GIGACPO V7.0 Production Snapshot — 2026-04-14]
