# 📋 CPO Dashboard Task List

## 🚀 Next Sprint

### 🔍 Pending / Future Work
- [ ] **OPENBB SUPPLEMENT — FETCH DATA**: Run `python engine/openbb_fetcher.py` to actually populate `openbb_supplement{}` for all 113 public equities. Uses yfinance (installed), OpenBB optional. Rate-limited at 1.5s per ticker (~3min total).
  - To fetch specific tickers: `python engine/openbb_fetcher.py --tickers CRDO BESIY ASMVY`
  - To refresh all: `python engine/openbb_fetcher.py --force`
  - Dry run to preview: `python engine/openbb_fetcher.py --dry-run`
- [ ] **DASHBOARD DISPLAY — openbb_supplement**: Once data is fetched, update cpo_plays.html to display `analyst_count` and `inst_ownership_pct` as small inline pills in the Research Info column.
- [ ] **NITTO BOSEKI**: Add Japan substrate/glass fiber play — already 2x+ YTD per Serenity research.
- [ ] **UNIMICRON**: Add Taiwan PCB/substrate play — already 2x+ YTD per Serenity research.
- [ ] **SKC ABSOLICS**: South Korea glass substrate — check if already in DB or add.
- [ ] **Re-run `scratch/audit_full.py`** after each major data change to maintain zero-issue audit.

### 🛠️ Data Infrastructure
- [x] Refactor to Authoritative JSON Architecture (V4.1) - Single Source of Truth.
- [x] Implement Global Exchange Heuristics (Retry logic for .TWO, .HK, .DE, etc.).
- [x] Capture Deep Financials (Margins, FCF, Debt, P/E).
- [x] Auto-sync JSON to CSV & HTML Dashboard (V4.2).

### 🎨 UI/UX & Visuals
- [x] Integrate Chart.js visual (Risk/Reward Scatter Plot).
- [x] Dashboard Upgrade (V4.3): Expandable sub-rows & Expert Mode.
- [x] Full Ecosystem Audit (V4.7): Restored global regions (US/JP/HK/TW), 1y calculated returns, and stabilized Rev Growth fallbacks.
- [x] Production Hardening (V4.8): Global Exchange harmonization (Collapsed 22+ down to Big 7), XSS protection, and Note legibility upgrade.
- [x] Intelligence Restoration (V4.9): Restored 'Best Plays' weighted ranking, Aggressiveness Slider (1-10), and 'Target Upside' column.
- [x] **V5.1 'Scorched Earth' Hardening**: Purged generic proxies ($NVDA, $SMCI, $NET, $AMD, $DELL, $HPE, $VRT, $OKTA, $T, $VZ, $CRWD, $ACN, $AAPL, $MSFT, $SNOW, $PLTR, $GOOGL, $META). Only 100% pure SiPh/CPO plays remain.
- [x] **V5.1 Intelligence Deep-Dive**: Re-ranked terminal based on ASE/TSMC CPO plant bottlenecks (Die Bonding, ABF Film, Glass Core).
- [x] **V5.1 Risk/Hiddenness Integration**: Added dedicated columns for Risk and Hiddenness as first-class citizens with 100% data coverage (113/113 stocks).
- [x] **V5.2 Terminal Consolidation (cpo_plays.html)**: Merged V5.1 terminal_v2_panel.html into cpo_plays.html as single production output. Archived terminal_v1_bar.html, terminal_v2_panel.html, terminal_v48.html to /archive/.
- [x] **V5.2 Private Watchlist Section**: Private/acquired companies (AYAR, RANV, CelestialAI, SCINTIL) given "Private" bucket (weight=0 in ranking), shown in purple-styled watchlist section below main table with 🔒 badge.
- [x] **V5.3 Ranking Engine Redesign**: Fixed critical sortDir=+1 bug (was ascending, should be descending). ETF bucket multiplier 0.22x (vs 1.0x for Core/Alpha). Aggressiveness slider ALWAYS resets to 'best' sort and immediately re-ranks. Momentum score rewards proven movers (40-200% 1y return = sweet spot, gets score 9-10). Rank numbers shown in table.
- [x] **V5.3 OpenBB Fetcher**: Built `engine/openbb_fetcher.py` — adds analyst estimates + institutional ownership + short interest as ADDITIVE supplement data. Never overwrites existing yfinance data. SKIP_TICKERS prevents fetching for private/ETF/irrelevant tickers.
- [x] **V5.3 Test Suite**: 12/12 tests passing (2 live tests skipped by design). Tests cover skip logic, yfinance mocking, dry-run safety, schema integrity, field conflict prevention.
- [x] **V5.3 Handoff Generator**: `generate_handoff.bat` — double-click to regenerate `gigacpo_llm_handoff.md` anytime.

### 🗄️ Data Quality V5.2
- [x] **AJINY Bucket Fix**: Changed from "AI Hub" to "Core". WHY IT WAS WRONG: Initial data population error — "AI Hub" was intended for demand-anchor companies (NVDA, AVGO, MRVL) that drive demand but don't supply CPO hardware. ABF film is a physical substrate requirement, NOT a demand consumption play. PREVENTION RULE: Any company whose Role contains "Film", "Substrate", "Material", "Chemical", "Equipment", or "Wafer" should NEVER be in AI Hub bucket. AI Hub = demand anchors only (companies that buy CPO, not make it).
- [x] **Score Format Fix**: Fixed 4 private company Risk Adj values stored as "60%/80%" (non-standard). Corrected to 0-10 scale.
- [x] **Missing Tickers Added**: $IPGP (IPG Photonics), $VIAVI (VIAVI Solutions), $CLFD (Clearfield), $LASR (nLIGHT) — 4 tickers from KNOWLEDGE.md research queue now in master data.
  - $IIVI: SKIPPED — II-VI merged into COHR (Coherent Corp) in 2022. Not a separate tradable entity.
- [x] **Total Universe**: Now 117 stocks (113 public + 4 private watchlist).

## ✅ Completed Tasks
- [x] Expand dataset to 100+ plays (117 total, 16 supply chain layers + Private watchlist).
- [x] Create automated `KNOWLEDGE.md` sync.
- [x] Stealth Stealth Stealth (Ghost Mode V2.8).
- [x] Create automated `start.bat` launcher.
- [x] Portfolio strategy engine (1-3yr timeline, 1-10 aggressiveness).
- [x] Must Watch ` 🔥` badges for 10x potential plays.
- [x] LLM Handoff Document: `gigacpo_llm_handoff.md` — 49KB complete context for peer LLM research validation.

## 🐛 Known Issues / ISSUES Log
- **JS/JSON Size Mismatch (EXPECTED)**: `dashboard_data.js` uses a compact subset of the full CPO_MASTER_DATA.json schema. The JS omits some deeply nested financial history arrays. This is by design for performance — the terminal only needs human_research + summary financials. NOT a bug.
- **IIVI ticker MISSING**: II-VI Technologies merged into Coherent Corp (COHR) in 2022. The IIVI ticker no longer trades. Covered by COHR entry in master data.
- **OpenBB v4.7.1 installed but not integrated**: Next sprint. Key additional data: analyst estimates, institutional ownership, multi-provider fundamental ratios. See "Pending / Future Work" above.

- [x] V6.1 Dashboard Fix: Resolved 'Shadow Crash' caused by 0y/+1y P/E mapping mismatch and JS column parity (16 headers vs 16 cells). Introduced strict 'Matrix Alignment' QA rule.
- [x] V6.1 Price Detection: Hardened P/E calculations using `LIVE_PRICES` fallback (fixes 0.0 P/E bug).
- [x] V6.1 Research Integration: Added Browave (Fiber Shuffle), LPKF (Glass Substrates), SIVE (Runway/M&A), and Win Semi (Avago stake).

## 📏 Data Quality Rules (ENFORCED)
- **AI Hub bucket ONLY for**: Companies that consume/buy CPO (NVDA, AVGO, MRVL) — demand anchors only.
- **Core bucket for**: Companies that physically produce a required component (materials, equipment, substrates).
- **Any company with Role containing "Film/Substrate/Material/Chemical/Equipment/Wafer" = NEVER AI Hub**.
- **Private bucket weight = 0**: Private/acquired companies always appear in separate Watchlist section, never inflate public equity rankings.
# 📋 CPO Dashboard Task List

## 🚀 Next Sprint

### 🔍 Pending / Future Work
- [ ] **OPENBB SUPPLEMENT — FETCH DATA**: Run `python engine/openbb_fetcher.py` to actually populate `openbb_supplement{}` for all 113 public equities. Uses yfinance (installed), OpenBB optional. Rate-limited at 1.5s per ticker (~3min total).
  - To fetch specific tickers: `python engine/openbb_fetcher.py --tickers CRDO BESIY ASMVY`
  - To refresh all: `python engine/openbb_fetcher.py --force`
  - Dry run to preview: `python engine/openbb_fetcher.py --dry-run`
- [ ] **DASHBOARD DISPLAY — openbb_supplement**: Once data is fetched, update cpo_plays.html to display `analyst_count` and `inst_ownership_pct` as small inline pills in the Research Info column.
- [ ] **NITTO BOSEKI**: Add Japan substrate/glass fiber play — already 2x+ YTD per Serenity research.
- [ ] **UNIMICRON**: Add Taiwan PCB/substrate play — already 2x+ YTD per Serenity research.
- [ ] **SKC ABSOLICS**: South Korea glass substrate — check if already in DB or add.
- [ ] **Re-run `scratch/audit_full.py`** after each major data change to maintain zero-issue audit.

### 🛠️ Data Infrastructure
- [x] Refactor to Authoritative JSON Architecture (V4.1) - Single Source of Truth.
- [x] Implement Global Exchange Heuristics (Retry logic for .TWO, .HK, .DE, etc.).
- [x] Capture Deep Financials (Margins, FCF, Debt, P/E).
- [x] Auto-sync JSON to CSV & HTML Dashboard (V4.2).

### 🎨 UI/UX & Visuals
- [x] Integrate Chart.js visual (Risk/Reward Scatter Plot).
- [x] Dashboard Upgrade (V4.3): Expandable sub-rows & Expert Mode.
- [x] Full Ecosystem Audit (V4.7): Restored global regions (US/JP/HK/TW), 1y calculated returns, and stabilized Rev Growth fallbacks.
- [x] Production Hardening (V4.8): Global Exchange harmonization (Collapsed 22+ down to Big 7), XSS protection, and Note legibility upgrade.
- [x] Intelligence Restoration (V4.9): Restored 'Best Plays' weighted ranking, Aggressiveness Slider (1-10), and 'Target Upside' column.
- [x] **V5.1 'Scorched Earth' Hardening**: Purged generic proxies ($NVDA, $SMCI, $NET, $AMD, $DELL, $HPE, $VRT, $OKTA, $T, $VZ, $CRWD, $ACN, $AAPL, $MSFT, $SNOW, $PLTR, $GOOGL, $META). Only 100% pure SiPh/CPO plays remain.
- [x] **V5.1 Intelligence Deep-Dive**: Re-ranked terminal based on ASE/TSMC CPO plant bottlenecks (Die Bonding, ABF Film, Glass Core).
- [x] **V5.1 Risk/Hiddenness Integration**: Added dedicated columns for Risk and Hiddenness as first-class citizens with 100% data coverage (113/113 stocks).
- [x] **V5.2 Terminal Consolidation (cpo_plays.html)**: Merged V5.1 terminal_v2_panel.html into cpo_plays.html as single production output. Archived terminal_v1_bar.html, terminal_v2_panel.html, terminal_v48.html to /archive/.
- [x] **V5.2 Private Watchlist Section**: Private/acquired companies (AYAR, RANV, CelestialAI, SCINTIL) given "Private" bucket (weight=0 in ranking), shown in purple-styled watchlist section below main table with 🔒 badge.
- [x] **V5.3 Ranking Engine Redesign**: Fixed critical sortDir=+1 bug (was ascending, should be descending). ETF bucket multiplier 0.22x (vs 1.0x for Core/Alpha). Aggressiveness slider ALWAYS resets to 'best' sort and immediately re-ranks. Momentum score rewards proven movers (40-200% 1y return = sweet spot, gets score 9-10). Rank numbers shown in table.
- [x] **V5.3 OpenBB Fetcher**: Built `engine/openbb_fetcher.py` — adds analyst estimates + institutional ownership + short interest as ADDITIVE supplement data. Never overwrites existing yfinance data. SKIP_TICKERS prevents fetching for private/ETF/irrelevant tickers.
- [x] **V5.3 Test Suite**: 12/12 tests passing (2 live tests skipped by design). Tests cover skip logic, yfinance mocking, dry-run safety, schema integrity, field conflict prevention.
- [x] **V5.3 Handoff Generator**: `generate_handoff.bat` — double-click to regenerate `gigacpo_llm_handoff.md` anytime.

### 🗄️ Data Quality V5.2
- [x] **AJINY Bucket Fix**: Changed from "AI Hub" to "Core". WHY IT WAS WRONG: Initial data population error — "AI Hub" was intended for demand-anchor companies (NVDA, AVGO, MRVL) that drive demand but don't supply CPO hardware. ABF film is a physical substrate requirement, NOT a demand consumption play. PREVENTION RULE: Any company whose Role contains "Film", "Substrate", "Material", "Chemical", "Equipment", or "Wafer" should NEVER be in AI Hub bucket. AI Hub = demand anchors only (companies that buy CPO, not make it).
- [x] **Score Format Fix**: Fixed 4 private company Risk Adj values stored as "60%/80%" (non-standard). Corrected to 0-10 scale.
- [x] **Missing Tickers Added**: $IPGP (IPG Photonics), $VIAVI (VIAVI Solutions), $CLFD (Clearfield), $LASR (nLIGHT) — 4 tickers from KNOWLEDGE.md research queue now in master data.
  - $IIVI: SKIPPED — II-VI merged into COHR (Coherent Corp) in 2022. Not a separate tradable entity.
- [x] **Total Universe**: Now 117 stocks (113 public + 4 private watchlist).

## ✅ Completed Tasks
- [x] Expand dataset to 100+ plays (117 total, 16 supply chain layers + Private watchlist).
- [x] Create automated `KNOWLEDGE.md` sync.
- [x] Stealth Stealth Stealth (Ghost Mode V2.8).
- [x] Create automated `start.bat` launcher.
- [x] Portfolio strategy engine (1-3yr timeline, 1-10 aggressiveness).
- [x] Must Watch ` 🔥` badges for 10x potential plays.
- [x] LLM Handoff Document: `gigacpo_llm_handoff.md` — 49KB complete context for peer LLM research validation.

## 🐛 Known Issues / ISSUES Log
- **JS/JSON Size Mismatch (EXPECTED)**: `dashboard_data.js` uses a compact subset of the full CPO_MASTER_DATA.json schema. The JS omits some deeply nested financial history arrays. This is by design for performance — the terminal only needs human_research + summary financials. NOT a bug.
- **IIVI ticker MISSING**: II-VI Technologies merged into Coherent Corp (COHR) in 2022. The IIVI ticker no longer trades. Covered by COHR entry in master data.
- **OpenBB v4.7.1 installed but not integrated**: Next sprint. Key additional data: analyst estimates, institutional ownership, multi-provider fundamental ratios. See "Pending / Future Work" above.

- [x] V6.1 Dashboard Fix: Resolved 'Shadow Crash' caused by 0y/+1y P/E mapping mismatch and JS column parity (16 headers vs 16 cells). Introduced strict 'Matrix Alignment' QA rule. Fixed fatal SyntaxError (re-declaration of `const live`).
- [x] V6.1 Price Detection: Hardened P/E calculations using `LIVE_PRICES` fallback (fixes 0.0 P/E bug).
- [x] V6.1 Research Integration: Added Browave (Fiber Shuffle), LPKF (Glass Substrates), Sivers (Runway/M&A), and Win Semiconductors (Avago stake).
- [x] Repository Initialization: Initialized git and pushed to `https://github.com/teeesss/ai_stock_plays`.


## 📏 Data Quality Rules (ENFORCED)
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
