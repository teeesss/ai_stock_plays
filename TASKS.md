# 📋 CPO Dashboard Task List

## 🚀 Next Sprint — V7.3: Visual Intelligence & OCR

### 🔍 X-Intelligence Hardening
- [x] **V7.6 BACKFILL & CATEGORIZATION**: 
  - [x] **KawzInvests**: 180-day backfill complete. Images categorized in `images/KawzInvests/`.
  - [x] **PhotonCap**: Loop issue resolved in V8.1. Full image backfill triggered (425+ images archived in `images/PhotonCap/`).
  - [ ] **aleabitoreddit**: Backfill pending.
- [x] **SCRAPER HARDENING (V8.1)**:
  - [x] **Loop Detection**: Implemented `seen_cursors` set to catch multi-cursor circular pagination.
  - [x] **Stale Page Detection**: Script stops after 3 consecutive pages with 0 new posts (prevents Nitter reload loops).
  - [x] **Image Sync Architecture**: Refactored `download_images` to sync ALL posts in user JSON, ensuring missing images are backfilled even if posts were already scraped.
  - [x] **Categorization**: Enforced `images/<username>/` directory structure for all downloads.
- [✅] Hardening: Scraper V8.6 Forward Harvest (Complete Historical Bridge)
- [✅] Cleanup: Purged 'Whoops' artifacts and fixed JSON serialization
- [✅] Backfill: `@aleabitoreddit` (Forward Harvesting October-January)
- [✅] Backfill: `@PhotonCap` (Forward Harvesting enabled)
- [ ] **OCR INTEGRATION**: Process archived images for ticker symbols and sentiment.

### 🛠️ Data Infrastructure & Integration
- [ ] **OPENBB SUPPLEMENT — FETCH DATA**: Run `python engine/openbb_fetcher.py`.
- [ ] **DASHBOARD DISPLAY — openbb_supplement**: Update UI to show analyst counts/inst ownership.
- [ ] **CHART INTEGRATION**: Line chart for Buzz Momentum.
- [ ] **NITTO BOSEKI**: Add Japan substrate/glass fiber play.
- [ ] **UNIMICRON**: Add Taiwan PCB/substrate play.
- [ ] **SKC ABSOLICS**: South Korea glass substrate — check if already in DB or add.
- [ ] **Re-run `scratch/audit_full.py`** after each major data change to maintain zero-issue audit.

## 📏 Data Quality Rules (ENFORCED)
### ✅ Completed Infrastructure (V4 - V6)
- [x] Refactor to Authoritative JSON Architecture (V4.1).
- [x] Stealth Navigator V2.8 (Playwright + curl_cffi hybrid).
- [x] Portfolio strategy engine & Aggressiveness Slider (V5.3).
- [x] Global Exchange Heuristics $Big-7 Consolidation$ (V4.8).
- [x] Matrix Alignment QA Rule (Prevents dashboard UI collapse).

### 🐛 Resolved Issues
- [x] **Pagination & Cursor Loops (V8.3)**: (Apr 2026) Wrote automated Search timeline fallback triggers into Nitter engine when a block or loop is detected. Scraper now bypasses bad cursors securely.
- [x] **PhotonCap Loop**: (Apr 2026) Resolved infinite pagination loop by tracking cursor history and implementing 3-page stale detection.
- [x] **Image Contamination**: Resolved loose image issue by enforcing `images/<username>/` structure.
- [x] **Yahoo 401 Unauthorized**: Bypassed by switching to `StealthNavigator` + `curl_cffi` for all data fetching.

## 📏 Data Quality Rules (ENFORCED)
- **AI Hub bucket ONLY for**: Companies that consume/buy CPO (NVDA, AVGO, MRVL).
- **Core bucket for**: Physical production (substrates, equipment, fiber).
- **Forbidden Tickers**: No generic AI proxies ($NVDA, $SMCI, $AMD).
- **Matrix Alignment**: `<thead>` MUST match `<tbody>` JS template cell count exactly.
- **Stale Protection**: Scraper must stop if dates don't progress or content is 100% duplicate.
- **AI Hub bucket ONLY for**: Companies that consume/buy CPO (NVDA, AVGO, MRVL) — demand anchors only.
- **Core bucket for**: Companies that physically produce a required component (materials, equipment, substrates).
- **Any company with Role containing "Film/Substrate/Material/Chemical/Equipment/Wafer" = NEVER AI Hub**.
- **Private bucket weight = 0**: Private/acquired companies always appear in separate Watchlist section, never inflate public equity rankings.
- **Forbidden tickers** (zero tolerance): $NVDA, $AMD, $SMCI, $HPE, $DELL, $VRT, $AAPL, $MSFT, $META, $GOOGL, $PLTR, $SNOW, $T, $VZ, $OKTA, $CRWD, $ACN, $NET.
- **Run `scratch/audit_full.py` after every major data change.** Zero criticals = green light.

- **BUG PREVENTION - Dashboard Matrix Alignment**: Any change to `<thead>` headers in `cpo_plays.html` MUST be immediately mirrored in BOTH the `pub.forEach` and `priv.forEach` JavaScript template loops. Failure to align column counts ($16 th == 16 td$) causes a silent UI collapse.
- **BUG PREVENTION - P/E data missing**: The earningsTrend module MUST be in all YF API module strings. If omitted from v10/quoteSummary, P/E 26 and P/E 27 show --. Fixed in financial_auditor.py and data_discovery.py.
- **BUG PREVENTION - Compound Ticker Fetching**: All engine files must call clean_ticker(ticker) before HTTP requests. Passing compound format like SIVE.ST / SIVEF directly to yfinance causes silent 404s.
- **BUG PREVENTION - Shadow Crash & Syntax**: Any new column added to the JSON schema must be explicitly handled in the JS template string. NEVER redeclare variables (e.g., `const live`) already defined in the loop scope as this causes a fatal SyntaxError in strict mode, resulting in an empty dashboard.

- **Duplicate detection**: Run scratch/migrate_tickers.py after any bulk data addition.
- **Browser Verification**: ALWAYS use a browser subagent to verify `cpo_plays.html` rendering after modifying JS data structures or HTML table layouts. Do not assume 'passing' python tests verify the UI.
