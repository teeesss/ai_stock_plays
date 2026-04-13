# CLAUDE.md — COS & CPO Stock Plays Project Rules

> **Purpose**: This file defines the rules, expectations, design standards, and research methodology for the COS/CPO Supply Chain Stock Plays project. Every AI session working in this workspace MUST read and follow these rules.

---

## 🚨 CRITICAL RULES

### 1. File Structure (Core)
- **Root**: Dashboards (`.html`), Master CSV, Documentation (`.md`), Launchers (`.bat`).
- **engine/**: Python implementation scripts and system automation logic.
- **tests/**: ALL test scripts (`test_*.py`, `verify_*.py`, `dashboard.test.js`).
- **database/**: Authoritative Master Data (`.json`), session state (`.json`), bridge data (`.js`), and auto-generated bundles.
- **logs/**: System and audit logs (`.log`).
- **research/**: **RESERVED FOR USER**. Only `.txt` and `.md` files created manually by the user. NO auto-generated or system files allowed here.
- **backup/**: Weekly snapshots of the Master JSON and CSV.

### 2. Never Lose Data
- **ALWAYS** append new research to `knowledge.md` — never overwrite prior findings.
- Every new stock, thesis, or data point discovered must be captured in `knowledge.md` with a timestamp.

### 3. Research Standards
- **Monopolies, duopolies, and micro-caps with massive room to run** are the highest priority.

### 4. X-Intelligence (Scraper) Logic
- **Forward Harvest Mode (V8.6)**: Use targeted chronological forward jumps (`since` -> `until`) for deep historical backfilling. This bypasses the Nitter pagination index bugs.
- **Garbage Purge**: Automatically filter out "Whoops...", "Fetching...", and Nitter block messages from the production database.
- **Loop Prevention & Fallback**: Track `seen_cursors` and apply a 3-page 0-post stale detection limit. If caught in a loop, pivot to Search Fallback to bypass defective timeline pagination safely. Do NOT simply terminate the scrape without triggering the fallback.
- **Instance Rotation**: Cycle instances (`LIVE_INSTANCES`) automatically upon fatal blocks.
- **Categorization**: Images MUST be stored in `images/<username>/`.
- **Text Formatting**: All text must pass through `clean_text_spacing` to enforce spaces around `$TICKERS` and `@USERNAMES`.
- **JSON Integrity**: Save with `indent=2` and `ensure_ascii=False` (un-escaped Unicode).
- **Deduplication**: Automatic ID-based deduplication on every save.

---

## 📐 Design & Layout Standards

### HTML Documents (`cpo_plays.html`)
- **ALWAYS use the premium dark theme** (dark bg `#0f172a`, card bg `#1e293b`, accent `#38bdf8`, gold headers `#fbbf24`).
- Must operate as a **Dynamic JS-Driven Dashboard**, utilizing `database/dashboard_data.js`.

---

## 🗂️ File Structure Mapping

```
z:/COS_Stock_Plays/
│
├── CLAUDE.md                      ← Rules & standards
├── TASKS.md                       ← Active and completed tasks
├── cpo_plays.html                 ← Interactive tactical terminal
├── cpo_master_ultimate.csv        ← Master dataset summary
├── start.bat                      ← One-click execution script
│
├── engine/                        ← Implementation Logic
│   ├── stealth_navigator.py       ← Ghost Mode engine (V4.4)
│   ├── financial_auditor.py       ← Deep intelligence extraction
│   └── generate_CPO_BRAIN.py      ← Master Sync Engine
│
├── tests/                         ← Test Gallery
│   ├── test_yfinance.py           ← Network validation
│   └── verify_stealth.py          ← Fingerprint validation
│
├── database/                      ← System Data (NO USER ENTRY)
│   ├── CPO_MASTER_DATA.json       ← Single Source of Truth
│   ├── dashboard_data.js          ← JS Data Bridge
│   └── CPO_BRAIN.json             ← LLM Context
│
├── logs/                          ← Error & Audit logs
│
├── research/                      ← USER RAW DATA ONLY
│   └── *.txt / *.md               ← User thoughts/notes
│
├── environment/                   ← Coding standards & environment config
└── backup/                        ← Critical file snapshots
```

---

**Last Updated**: 2024-04-12 (V8.1 Scraper Hardening & Image Categorization)
**Review**: At the start of every session
**Enforcement**: Mandatory
