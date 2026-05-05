# Project Status: Sovereign Intelligence Engine

## 🚀 Current Milestone: V30.6.10 — Cross-Channel Pricing Parity [2026-05-05]
- **Single Source of Truth**: `ticker_utils.py` is now the authoritative module for ALL ticker legitimacy checks (`is_legit_ticker`), session data (`get_ticker_session_data`), and valuation rendering (`render_valuation_row`).
- **News/Email Parity**: Both `/news` and `/email` portals now consume the identical pricing and session logic — zero divergence.
- **Preposition Flair Fix**: `TICKER_BLACKLIST` in `ticker_utils.py` now includes common English words (ON, AT, BY, IF, IN, TO, OF...) preventing false price flair in news headlines.
- **Ticker Cockpit (V30.6.9)**: Dashboard decoupled to `engine/ticker_dashboard.py`. Columns: PRICE | AH/OVN/PRE/L | % CHG | CLOSE | C % | MCAP | '26 P/E | '27 P/E.

Status: **PRODUCTION DEPLOYED — VERIFIED ✅ 2026-05-05**

---

## 🚀 Version: V30.4.19 (Unified Narrative & Anchor Fidelity)
Status: **PRODUCTION DEPLOYED — VERIFIED ✅ 2026-05-05**

📊 **Project Status: Sovereign Intel**
- **Current Tier**: V30.6.10 (Cross-Channel Pricing Parity)
- **Critical Progress**: News and email pipelines now share identical pricing, session, and valuation logic.
- **Next Milestone**: V30.7 — Automated sector-specific weighting for narrative generation.

Date: 2026-05-05
Tests: **158 passing / 0 failing ✅**

---

## Architecture Hierarchy (V30.6.10)

| File | Role |
|------|------|
| `engine/ticker_utils.py` | **SINGLE SOURCE OF TRUTH** — pricing, session, valuation, legitimacy |
| `engine/ticker_dashboard.py` | Ticker Cockpit HTML + CLI rendering engine |
| `engine/email_market_synopsis.py` | Sovereign Email Intelligence Engine |
| `engine/news_market_synopsis.py` | News Portal Engine (mirrors email, uses same pricing) |
| `engine/live_prices.py` | Async price fetcher → `database/live_prices.json` |
| `engine/market_session.py` | Session/temporal authority (PRE/LIVE/AH/OVN/CLOSED) |
| `engine/error_monitor.py` | Error tracking authority (atexit integration) |
| `engine/remote_sync.py` | SFTP deployment → bmwseals.com |

## URL Routing
| URL | Source File |
|-----|-------------|
| `bmwseals.com/stocks/email` | `database/synopsis_preview.html` |
| `bmwseals.com/stocks/news` | `database/news_preview.html` |
| `bmwseals.com/stocks/tickers.html` | `database/tickers_preview.html` |
| `bmwseals.com/stocks/ai` | `web/ai/index.html` |

---

### Known Rules (Lessons Learned)
- `passesFilters()` P/E sentinel: **999 = no EPS data**. Max filter active → exclude 999. Min-only → allow.
- OBB fields: always use null-safe `?.` access before calling sfloat().
- Buzz counts are **integers**, not floats. Always use `parseInt(val, 10)`.
- Never define the same function name twice in `cpo_plays.html`.
- Dashboard data is minified JSON on a single line — edits must be surgical via engine scripts, not manual.
- **V30.2 Hardening**: Always strip HTML from RSS summaries before NLP splitting to avoid corrupted link fragments.
- **V30.6.10 Rule**: NEVER duplicate `is_legit_ticker` or session logic in individual engines. ALL legitimacy and session checks must come from `ticker_utils.py`.
- **V30.6.10 Rule**: When refactoring a class, always verify `_load_json` and other utility helpers survive the edit.
- **V30.6.7 Rule**: Engine scripts on NAS drives (X:) must NOT be executed via `wsl` or `bash`. Use PowerShell native only. Launcher shell scripts delegate to Python engines to avoid Windows security warnings.

[GIGACPO V30.6.10 Production Snapshot — 2026-05-05]
