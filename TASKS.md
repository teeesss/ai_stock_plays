# 🎯 X-Intelligence: Project Roadmap

### 🚀 Current Status: V17.1 (Hardened Sync + Performance Bridge)
- **Deployment**: Flattened SFTP structure targeting root `/stocks/` to eliminate script 404s.
- **Performance**: Deferred JS hydration logic + Paginated News rendering (50-item limit).
- **Hardening**: Standardized paramiko-based push.
- **Data Integrity**: Institutional Whale conviction + SiPh News universe parity (6,900 articles).
- Date: 2026-04-17

- **Data Integrity**: China-only stocks (INNO, EOPT) reclassified → Private/no_dashboard.
- **Image Pipeline**: OCR → `processed_images.json` → `visual_intel[]` per post → `visual_mentions` in master.
- **Dashboard**: Visual buzz (📷) badges alongside tweet buzz (𝕏) in buzz bar + row chips.
- **Scraper Safety**: `visual_intel` now survives `_deduplicate_file` and `_incremental_save` rewrites.
- **Orchestration**: `x_intel_daily_sync.py` auto-runs image_analyzer + visual_buzz_aggregator post-scrape.
- **Durability**: `rebuild_master()` now carries forward `visual_mentions` — OCR work never lost on rebuild.
- **Unicode**: All JSON writes use `ensure_ascii=True` — no more VS Code ambiguous-unicode warnings.
- **Logging**: Python scripts now autonomously output to `logs/*.log` to prevent debugging noise.
- **Scraper Search**: Fixed Nitter date constraint parsing to prevent recursive vintage deep fetches.
- **Quality**: 7-day lookback filtering active for news sanity.
- **Deduplication**: SHA-256 Title-based news deduplication verified.
- **Architecture**: Move to root-flattened deployment on bmwseals.com.
- Date: 2026-04-17

---

## 🛠 Active Tasks

- [x] **Task 2: Expanded X Search Filtering** — Added Username select and Date From/To inputs to dashboard; updated `x_intel_deep_scraper.py` with CLI flags (`--since`, `--until`, `--query`).
- [x] **Task 3: Username Management Script** — Created `engine/manage_users.py` and `database/monitored_users.json` for dynamic user tracking.
- [x] **Task 4: BetterTwitFix Integration** — Implemented `engine/vx_rescue_fetcher.py` and integrated into scraper as a fallback repair layer for truncated/broken tweets.
- [x] **Task 5: Image Intelligence Hardening** — Removed OCR batch limits in `image_analyzer.py`; modernized `visual_buzz_aggregator.py` to handle all monitored users dynamically.
- [x] **Task 6: Unified Terminal** — Created `terminal.py` menu system for orchestrating all 11 engine scripts.
- [x] **Task 13F: Institutional Alpha** — Created `engine/inst_13f_fetcher.py` to pull 13F hedge fund positioning (WhaleRock, Altimeter, Coatue) into master data.
- [x] **Task LIDE: Glass Supercycle Mapping** — Created `engine/glass_intel_mapper.py` to map the LIDE/TGV supply chain (LPKF, Absolics, Corning) into the terminal.

---

## ✅ Completed — V15.4 Pipeline Durability + Unicode (2026-04-14)

- [x] **Merge ISSUES.md into TASKS.md**: Integrated historical issues and cleared ISSUES.md.
- [x] **Unicode fix (all writers)**: `ensure_ascii=False` → `True` in `rebuild_master.py`,
  `visual_buzz_aggregator.py`, and both write paths in `x_intel_deep_scraper.py`.
  All JSON files are now pure 7-bit ASCII; emojis/smart-quotes encoded as `\uXXXX`.
  Eliminates VS Code "ambiguous unicode characters" warning permanently.
- [x] **Durability fix — `rebuild_master.py`**: Now reads existing master's `visual_mentions`
  + `visual_last_updated` before overwriting. OCR aggregation data survives every rebuild.
- [x] **Durability fix — `x_intel_deep_scraper.rebuild_master()`**: Same carry-forward logic
  applied to the inline version called after each scrape run.
- [x] **`scratch/verify_pipeline.py`**: Quick sanity script — checks unicode, visual_mentions,
  intel.js, processed_images.json, and per-user visual_intel. Run any time to confirm health.
- [x] **Verified clean**: 6507 posts | 37 visual tickers | 560 OCR log entries | ALL CLEAR.
- [x] **Nitter Search Bug**: Switched literal `+` parameters to `%20` encoded spaces in deep scraper. Search queries `since` and `until` commands are now successfully enforced by nitter instead of ignored, stopping infinite loops fetching old tweets.
- [x] **Autonomous Audit Logging**: Scripts `x_intel_instant_sync.py`, `x_intel_daily_sync.py`, `x_intel_deep_scraper.py`, `x_intel_fetcher.py`, and `x_intel_auto_sync.py` now all execute FileHandlers sending debugging telemetry directly to `logs/` directory autonomously.

---

## 🐞 Historical Issues & Resolutions (from ISSUES.md)

- **[FIXED] BeautifulSoup/Playwright Missing Dependencies**: Scrapers failed on fresh Windows nodes.
  - **Resolution**: Created global `requirements.txt` and integrated `python -m playwright install chromium`.
- **[FIXED] Windows I/O Unicode Crash**: `ValueError: I/O operation on closed file` during translation.
  - **Resolution**: Implemented `io.TextIOWrapper` with error handling in `translate_intel.py`.
- **[FIXED] Ticker Fragmentation**: Mirror HTML caused $N V D A$ instead of $NVDA.
  - **Resolution**: Deployed V11.0 Surgical Regex with boundary detection.
- **[FIXED] Browser CORS Security Block**: Browser prohibits `fetch()` from local filesystem.
  - **Resolution**: Implemented JS Data Bridge (`research/sync_data.py`).
- **[OPEN] Data Gaps**: Revenue estimates for Tier-2 suppliers (AXTI, Sumitomo) are estimates.
  - **Status**: Research ongoing.

---

## ✅ Completed — V15.3 Visual Intelligence Pipeline (2026-04-14)

- [x] **China-only reclassification**: INNO (InnoLight) + EOPT (Eoptolink) → `Bucket: Private`,
  `Status: China-Only`, `no_dashboard: true`. Excluded from scoring, rankings, and price fetches.
  Remain in Private watchlist section for research tracking.
- [x] **Image processing forensic**: Confirmed 560/2517 total images processed overnight. 
  1,957 remaining images are new from tonight's scrape (not data loss — genuinely new downloads).
  `processed_images.json` is the durable skip-log; `visual_intel[]` per-post arrays are intact.
- [x] **`_deduplicate_file()` fix**: Now explicitly sets `visual_intel: []` on all posts,
  ensuring OCR data never silently evaporates through dedup or incremental save passes.
- [x] **`_incremental_save()` fix**: Merges `visual_intel` from existing posts by ID when
  combining new + existing post lists.
- [x] **`engine/visual_buzz_aggregator.py`**: New engine module — reads all `x_intel_<user>.json`
  `visual_intel[]` arrays, aggregates ticker OCR hits, merges `visual_mentions` dict into
  `x_intel_master.json` + rebuilds `intel.js`. First run: 684 hits across 555 images, 37 tickers.
- [x] **`x_intel_daily_sync.py` pipeline**: Post-scrape auto-runs Step 2 (image_analyzer OCR)
  + Step 3 (visual_buzz_aggregator) so every nightly run is fully self-contained.
- [x] **Dashboard — `no_dashboard` filter**: `buildEntries()` now skips entries with
  `no_dashboard: true` — INNO/EOPT never appear in ranked table or scoring.
- [x] **Dashboard — Visual buzz badges**: 📷 green badge added to row Role/Notes cell showing
  image hit count (alongside existing 𝕏 tweet buzz gold badge). Tooltip shows OCR sample text.
- [x] **Dashboard — Buzz bar upgraded**: `renderBuzz()` now merges tweet buzz (𝕏N) + visual
  mentions (📷N) into unified top-14 ranking. Both signal types visible per tag.

---

## ✅ Completed — V15.2 AH/PM Extended-Hours Column (2026-04-14)

- [x] **`live_prices.py`**: Capture `postMarketPrice`/`postMarketChangePercent` + `preMarketPrice`/`preMarketChangePercent` from Yahoo quote response (zero extra requests — same batch call). Stored as `ext_price`, `ext_pct`, `ext_type` (AH/PM).
- [x] **`cpo_plays.html`**: Added **AH / PM** column (sortable) showing label, ext price, and % move in green/red.
- [x] **Micro-timestamp**: `HH:MMZ` update time displayed above regular price cell so staleness is visible at a glance.
- [x] **Colspan**: Private watchlist divider bumped 16→17.
- [x] **Sort**: `ext` key wired into `sortFn` for AH/PM column sort.

---

## ✅ Completed — V15.1 Filter Integrity Sprint (2026-04-14)

### Bug Fixes (cc429cc)
- [x] **CRITICAL: Duplicate function definitions removed** — `filterIntel()`, `openIntelModal()`,
  `closeIntelModal()`, and `renderBuzz()` were defined TWICE in `cpo_plays.html` (lines 620+648).
  The second stub version silently overrode the correct first definition, breaking the Intel modal.
- [x] **P/E Filter — Sentinel bug fixed** — `pe26=999` / `pe27=999` are the sentinel for "no EPS data".
  Old code: `e.pe26 < state.maxPe26` incorrectly excluded no-data stocks when any filter was active.
  New code: max filter active → exclude 999; min-only filter → allow 999 through.
- [x] **OBB null-safe access** — `e.obb.inst_ownership_pct` crashed on stocks with no OBB data.
  Replaced with null-safe pattern + `hasInst`/`hasShort`/`hasAnalysts` guards.
- [x] **Buzz count parseInt** — `sfloat(e.buzz?.['7d'])` was parsing buzz counts as floats.
  Changed to `parseInt(..., 10)` to correctly handle integer mention counts.

### QA (2026-04-14)
- [x] **`tests/test_dashboard_filters.py` created** — 29 new tests covering:
  - `TestPEFilterLogic` (8 tests) — sentinel, range, min-only, regression
  - `TestOBBNullSafeFiltering` (8 tests) — null obb, empty string, range checks
  - `TestBuzzFilterParsing` (5 tests) — int string, raw int, None, zero, out-of-range
  - `TestHTMLStructuralIntegrity` (8 tests) — regex scan of actual HTML for duplicate defs,
    parseInt presence, hasInst/hasShort/hasAnalysts presence, 999 sentinel presence
- [x] **Full test suite: 50 tests — 100% passing**

---

## ✅ Completed — V15.0 Surgical Integrity (2026-04-14)

- [✅] Forensic: V11.0 Surgical Repair (Fixed Ticker Fragmentation & Word-Smashing)
- [✅] Dependency: Validated 100% environment compatibility via `requirements.txt`.

## Dashboard UI & Readability (V13.2)
- [x] Convert X-Intelligence Buzz Bar to horizontal orientation
- [x] Increase global font sizes for high-res desktop readability (11px -> 13px)
- [x] Fix vertical text issues in social intelligence search results
- [x] Execute UI/UX Accessibility Audit

## QA & Stability
- [x] Restore and standardize the automated test suite
- [x] Resolve test-collection errors and module pathing issues
- [x] Sync localized forensic logic with regression tests
- [x] Verify remote production webpage (bmwseals.com/stocks/)
- [x] Write QA tests for passesFilters() filter logic (P/E, OBB, Buzz, Duplicate Defs)

---

## 🔜 Open / Backlog

- [x] **INNO/EOPT Country tag fix** (2026-04-14): INNO corrected to `Country: China` — yfinance
  ticker "INNO" resolves to wrong NYSE entity; financials cleared, `no_yfinance: true` flagged.
  EOPT corrected to `Country: China`, `currency: CNY`, `real_ticker: 300502.SZ`. Both master
  JSON and `dashboard_data.js` updated.
- [x] **HBM4 Supply Chain Audit**: Expanded glass substrate mapping to include HBM4-specific interposers and back-end packaging (Besi, ASM Pacific).
- [x] **Automated Institutional Scoring**: Factored 13F conviction counts straight into the Alpha ranking algorithm in JS (`cpo_plays.html`).
- [x] **Real-time Price Engine 2.0**: Validated `live_prices.py` correctly fetches non-USD ADR equivalents (BESIY, ASMVY).

---

[✅] **Translation Cache**: Persistent `translation_cache.json` for zero-waste repeated runs.
[✅] **Remote Sync**: Automated SFTP deployment for production mirroring.
[✅] **GIGACPO BRAIN**: Updated SiPh/CPO master intelligence bridge.
[✅] **Filter QA**: 50-test automated regression suite covering core dashboard logic.
