# GIGACPO Technical Architecture (V22.94)

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
- **Scoring**: `Alpha` (High growth/upside/buzz), `Risk` (High P/E/short interest), `Hidden` (Low MCAP/Analyst count + High Growth).

### Layer 4: Pipeline Orchestrator (`pipeline_orchestrator.py`)
- **Role**: The centralized state-machine conductor.
- **Workflow**: Load Financials -> Normalize legacy fields -> Calculate dynamic scores -> Generate `dashboard_data.js` -> Deploy via SFTP to mapped nesting.

### Layer 5: Sovereign Intelligence Engine (`email_market_synopsis.py`)
- **Extractive NLP**: Uses `local_nlp.py` (LSA + VADER) for offline synthesis of market catalysts.
- **Signal Governance**: Implements a `NEWS_BLACKLIST` (e.g., Jim Cramer) to sanitize the ingestion pool.
- **Responsive Parity**: Employs `@media` independent styling definitions for Desktop (14-24px) vs Mobile (9-12px) typography.

---

## 3. Data Integrity & QA
- **Strict 15-Minute Protocol**: Verified by the `is_entity_fresh` helper. Ensures a 900s global TTL for all asset classes (Indices, Crypto, and news-discovered tickers), preventing Yahoo Finance rate-limiting and redundant fetching.
- **Surgical Regex**: `engine/forensic_repair.py` ensures tickers like $N V D A$ are collapsed to $NVDA.
- **P/E Sentinels**: Uses `999` for missing EPS data.
- **Self-Hydrating Discovery**: The engine scans narratives for tickers and force-hydrates stale/missing prices while strictly honoring the 15-minute global pulse.
- **Session-Aware Labeling**: Integrated `PM`/`AH` markers and `OVN` (Overnight) session detection. Uses high-fidelity BOATS data via `overnightPrice=true` to capture institutional-standard real-time prices while other sources remain stale.
- **Extended-Hours Cascade**: Prioritizes `OVN` (BOATS) > `PRE` > `POST`, ensuring the terminal reflects the most active trading state at all times.

---

## 4. UI Rendering System
- **Template-Driven**: Root and AI terminals use isolated `index_template.html` structures.
- **Dual-Surface Emails**: Liquid-table layouts with independent Desktop/Mobile scale definitions via CSS Media Queries.
- **High-Density Output**: Terminals use strict tables (13px); dossiers use scaled block-level tiles for multi-device readability.

---

## Technical Summary
- **Primary Languages**: Python 3.12+ / Vanilla JS / CSS3 (Grid/Flexbox/@media).
- **Extraction Engine**: `curl_cffi` (Chrome 146 Impersonation) + Playwright Stealth.
- **NLP Suite**: `sumy` (LSA), `vaderSentiment`, `scikit-learn` (TF-IDF).
- **Delivery**: SMTP (TLS 1.2) via Gmail App Passwords.
- **Data Model**: JSON persistence (UTF-8) with atomic transactional writes.
