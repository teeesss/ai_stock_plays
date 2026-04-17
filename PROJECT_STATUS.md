# Project Status — April 17, 2026
## 🚀 Version: V17.1 (Hardened Sync & Performance Bridge)

Status: **PRODUCTION DEPLOYED — SI-PH NEWS ACTIVATED**
Date: 2026-04-17
Tests: **52 passing / 0 failing**

---

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
- **Windows I/O Stability**: Fixed Unicode "I/O operation on closed file" errors.
- **Precision Sync**: `x_intel_instant_sync.py` verified 100% bug-free.
- **Broadened Detection**: Expanded ticker mapping regex from (3-6) to (2-12) chars.

---

### 🎯 Current Focus
1. **INNO Country Fix**: Change `"Country": "US"` → `"China"` for InnoLight (China A-share, not US-listed).
2. **Glass Substrate Supercycle**: Intensify LIDE/TGV analysis as HVM approaches (Intel/Samsung/ASE).
3. **13F Institutional Layer**: Automated tracking of top-tier hedge fund positioning in CPO names.

### 🏛️ Engineering Standard
- **Core Engine**: Scraper V11.0 + Forensic V14.1 + Hyper-Drive V12.6 + Visual Intel V1.0.
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
