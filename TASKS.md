# 🎯 X-Intelligence: Project Roadmap

### 🚀 Current Status: V15.1 (Filter Integrity & QA Hardening)
- **Data Integrity**: V11.0 Surgical Repair DEPLOYED. Ticker fragmentation collapsed.
- **Dashboard Filters**: V15.1 — `passesFilters()` logic fully corrected and QA-verified.
- **QA Coverage**: 50 automated tests across 4 suites. All passing.
- **Environment**: 100% dependency parity via `requirements.txt`.
- **Automation**: Platinum Core — SFTP deploy, translation hyper-drive, live prices active.
- Date: 2026-04-14

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

- [ ] **INNO Country tag**: InnoLight Technology is China A-share listed, not US.
  `"Country": "US"` in master data is incorrect. Fix to `"China"` + note no yfinance data.
- [ ] **13F Institutional Layer**: Automated tracking of top-tier hedge fund positioning in CPO names.
- [ ] **Glass Substrate Supercycle**: Intensify LIDE/TGV analysis as HVM approaches.
- [ ] **Automated Monitoring**: Weekly audit of translation cache and scrapers.

---

[✅] **Translation Cache**: Persistent `translation_cache.json` for zero-waste repeated runs.
[✅] **Remote Sync**: Automated SFTP deployment for production mirroring.
[✅] **GIGACPO BRAIN**: Updated SiPh/CPO master intelligence bridge.
[✅] **Filter QA**: 50-test automated regression suite covering core dashboard logic.
