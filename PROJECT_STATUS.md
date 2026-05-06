# Project Status: Sovereign Intelligence Engine

## 🚀 Current Milestone: V30.6.10 — Intelligence Pipeline Hardening [2026-05-05]
- **Hardened Ticker Engine**: `ticker_dashboard.py` now includes an **Auto-Dependency Guardian** (`dependency_mgr`) and robust import fallbacks to prevent "N/A" watchlist artifacts.
- **Session-Relative Momentum**: `% CHG` in extended sessions is now calculated against the **today's close** (momentum-only) rather than yesterday's close, aligning with institutional data standards.
- **Mobile Responsive Cockpit**: The web dashboard now dynamically collapses to 6 columns on mobile to maintain density and readability.
- **Extensionless Deployment**: Ticker dashboard is now served at `bmwseals.com/stocks/tickers` (extensionless) for a cleaner, professional URL structure.
- **Single Source of Truth**: `ticker_utils.py` remains the authoritative leader for session data, valuation rendering, and ticker legitimacy.

Status: **PRODUCTION DEPLOYED — VERIFIED ✅ 2026-05-05**

---

## 🚀 Version: V30.4.19 (Unified Narrative & Anchor Fidelity)
Status: **PRODUCTION DEPLOYED — VERIFIED ✅ 2026-05-05**

📊 **Project Status: Sovereign Intel**
- **Current Tier**: V30.6.10 (Intelligence Pipeline Hardening)
- **Critical Progress**: Watchlist engine hardened with dependency-awareness, momentum-relative pricing, and mobile-responsive high-density layouts.
- **Next Milestone**: V30.7 — Automated sector-specific weighting for narrative generation.

Date: 2026-05-05
Tests: **168 passing / 0 failing ✅**

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
| `bmwseals.com/stocks/tickers` | `database/tickers_preview.html` |
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
