# Sovereign Intelligence Email Synopsis Guide (V23.59)

## 📖 Overview
`email_market_synopsis.py` is the primary orchestrator for the Sovereign Intelligence Engine. It synthesizes global market signals, real-time price action, and news sentiment into a high-density "Intelligence Dossier" delivered via SMTP.

---

## 🚀 Usage & CLI Flags

### Base Commands
- **Generate Local Preview Only**: 
  ```bash
  python engine/email_market_synopsis.py
  ```
  *(Generates `database/synopsis_preview.html`)*

- **Dispatch Email**:
  ```bash
  python engine/email_market_synopsis.py --test-email
  ```

### Advanced Ticker Targeting
- **Explicit Comma-separated List**:
  ```bash
  python engine/email_market_synopsis.py --tickers NVDA,AMD,AAPL
  ```
- **Load from Text File**:
  ```bash
  python engine/email_market_synopsis.py --tickers tickers.txt
  ```
- **Fierce Flag Syntax**:
  ```bash
  python engine/email_market_synopsis.py --NVDA --TSMC --ASML
  ```

---

## 🧩 Core Intelligence Modules

### 1. Sovereign Index Pulse (US & Global)
- **Timezone Normalized (V23.58)**: All session detection is normalized to **US/Eastern (EST)**. 
- **Time-Anchored Windows (V23.86)**: Forces correct session data even if Yahoo flags are stale.
- **Index Futures (V23.86)**: Automatically switches to `ES=F`, `NQ=F`, `YM=F` during extended hours.
- **Session Badges**: 
  - `L⚡` (Green): Regular Market.
  - `PRE` (Orange): Pre-market (4 AM - 9:30 AM EST).
  - `AH` (Red): After-hours (4 PM - 8 PM EST).
  - `OVN` (Amber): Overnight / Sunday Futures (8 PM - 4 AM EST).

### 2. Narrative Intelligence (`local_nlp.py`)
- Uses **Latent Semantic Analysis (LSA)** to scan the headlines of target tickers.
- **Session-Aware Flair (V23.85)**: Headlines injected into the narrative now reflect active session prices (PRE/AH) instead of stale close data.

### 3. Sector Dossier Cards
- Maps tickers to specific sectors (Semiconductors, AI Infrastructure, Cloud).
- Prioritizes **conviction-weighted scoring** and 13F institutional signals.

---

## 🔍 Work Log Transparency (V23.86)
The script now provides high-fidelity diagnostic output during execution:
- **`[INFO] [CACHE]`**: Shows remaining TTL for news and prices.
- **`[INFO] [LIVE]`**: Confirms just-in-time data refreshes.
- **`[INFO] [ALPHA]`**: Previews the top-ranked insight selected by the NLP engine.

---

## 🛡️ Environment & Security

### Auto-Dependency Guardian (V23.59)
The script now automatically checks for mission-critical libraries (`bs4`, `playwright`, `curl-cffi`, etc.) on every startup. 
- **Interactive**: If missing, it will prompt to auto-install via `sys.executable`.
- **Non-Interactive**: Fails gracefully with a list of missing packages to prevent pipeline hangs.

### Authentication
Requires a `.env` file in the root with:
```env
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASS=your_gmail_app_password
RECIPIENT_EMAIL=target_email@gmail.com
GMAIL_DISPLAY_NAME="Sovereign Intel"
```

---

## ⚠️ Troubleshooting

### NAS/I/O Latency
The script is designed to run from network-attached storage (`/mnt/projects`). 
- **Lag**: You may experience a 15-90s delay as the `ticker_name_map.json` is loaded.
- **Heartbeat Logs**: High-resolution timestamps are enabled to profile which part of the ingestion is slow.

### Price Data-Void
If an asset shows `N/A`, it usually means the symbol was recently added and hasn't been hydrated. 
- **Force Hydrate**: Run `python engine/live_prices.py --tickers SYMBOL` to populate the cache immediately.

---
*Autonomous Status: STABLE // GIGACPO V23.59*
