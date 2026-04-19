# GIGACPO Technical Architecture (V20.0)

## Overview
Financial data is adversarial. Standard APIs (Standard & Poor's, FactSet) are expensive or laggy. Public scrapers (YFinance) are frequently blocked. GIGACPO solves this through a decoupled, multi-layered stealth architecture.

---

## 1. Core Principles (Bottom-Up)

### Indirection as a Feature
Never hit a target directly.
- **Yahoo Stealth Protocol**: Authentication and session crumbs are managed by `engine/yahoo_auth.py` using Playwright (Chromium). Static sessions are cached. Consumer fetchers (`live_prices.py`, `news_fetcher.py`) use these crumbs with `curl_cffi` to impersonate standard browser TLS fingerprints.
- **Static Artifacts**: The UI (JS/HTML) never queries a live database. All data is pre-baked into static `.js` files via the `PipelineOrchestrator`. This ensures 100% availability and sub-100ms load times.

---

## 2. Component Layers

### Layer 1: Stealth Authentication (`yahoo_auth.py`)
- **Mechanism**: Navigates to Yahoo Finance, solves basic consent popups, and extracts `cookies` and `crumb`.
- **Output**: `database/stealth_session.json`.
- **Reason**: Decouples the "heavy" browser requirement from "light" extraction workers.

### Layer 2: Modular Fetchers
- **`live_prices.py`**: Fetches real-time quotes in batches of 10. Handles ADRs ($ASMVY) and extended hours (AH/PM).
- **`news_fetcher.py`**: Pulls ticker-specific news. Implements SHA-256 deduplication and strict anti-spam regex.
- **`openbb_fetcher.py`**: Hydrates secondary metrics: Analyst upside, institutional ownership, short interest.

### Layer 3: Intelligence Engine (`intelligence_engine.py`)
- **Formula**: Bayesian-style percentile normalization.
- **Metrics**: MCAP, P/E, Analyst counts, Buzz counts, Revenue Growth.
- **Scoring**:
  - `Alpha`: High growth + High upside + High buzz.
  - `Risk`: High P/E + High short interest + Low Analyst support.
  - `Hidden`: Low MCAP + Low Analyst count + High Growth.

### Layer 4: Pipeline Orchestrator (`pipeline_orchestrator.py`)
- **Role**: The state-machine conductor.
- **Workflow**:
  1. Load Financials from master DB.
  2. Normalize field names (Growth, MCAP).
  3. Calculate dynamic scores.
  4. Generate `dashboard_data.js` artifact.
  5. Deploy via SFTP to production.

---

## 3. Data Integrity & QA
- **Surgical Regex**: `engine/forensic_repair.py` ensures tickers like $N V D A$ are collapsed to $NVDA without smashing surrounding text.
- **P/E Sentinels**: The logic uses `999` as a sentinel for missing EPS data. Dashboard filters are hardened to handle this (Max filter active -> exclude 999).
- **Automated Tests**:
  - `tests/test_dashboard_filters.py`: Verifies P/E, OBB, and Buzz filtering logic.
  - `tests/test_momentum_data.py`: Ensures 7-day trajectory bars are correctly calculated.

---

## 4. UI Rendering System
- **Template-Driven**: `AI/index_template.html` is the source of truth. `generate_ui.py` populates it with dynamic sector filters.
- **Zero-Padding Table**: The terminal uses a high-density table (13px font) designed for financial analysts.
- **Momentum Strips**: Visual trajectory bars (Green/Red dots) derived from the last 7 sessions of price action.

---

## Technical Summary
- **Language**: Python 3.10+ (Engine) / Vanilla JS (UI).
- **Auth**: Playwright (Headless).
- **Network**: `curl_cffi` (Impersonating Chrome 147).
- **Data**: JSON persistence with 7-bit ASCII encoding.
