# GIGACPO Sync & Update Guide (V22.44)

This guide documents the data pipeline for the GIGACPO Financial Intelligence Terminal and Sovereign Intelligence Engine.

## 🚀 Recommended Workflows

### 1. Daily Standard Refresh (Recommended)
Run this once or twice a day to ensure the website is fully up-to-date with Tweets, News, and Chart Analysis.
*   **Command:** `python engine/sync_triple.py` (or Option **[1]** in terminal)
*   **Action:** Scrapes last 24h of tweets, fetches 7-day Yahoo news, runs OCR on new images, and deploys to both Semi and AI web pages.

### 2. Fast Refresh (Low Resources)
Use this if you are in a hurry or on a slow connection.
*   **Command:** `python engine/sync_triple.py --skip-ocr`
*   **Action:** Updates everything except the Chart OCR data.

### 3. Sovereign Intelligence Dispatch
Specifically triggers the high-fidelity NLP email dossier.
*   **Command:** `python engine/email_market_synopsis.py`
*   **Action:** Hydrates latest Fear/Greed + Market Prices -> Performs Local NLP Synthesis -> Purges Cramer/Spam news -> Dispatches responsive email.

---

## 🏗️ Data Architecture

### Pillar 1: Tweets (X Intelligence)
*   **Script:** `engine/x_intel_deep_scraper.py`
*   **Logic:** Uses Nitter/Yahoo auth to bypass rate limits. It fetches raw JSONs per user.

### Pillar 2: Yahoo News & Local NLP
*   **Script:** `engine/sync_news.py` & `engine/local_nlp.py`
*   **Logic:** Pulls relative news and performs extractive summarization.
*   **Governance:** Implements `NEWS_BLACKLIST` to remove low-signal sensationalism (e.g. Jim Cramer).

### Pillar 3: Tactical Prices
*   **Script:** `engine/live_prices.py`
*   **Logic (V23.86):** **Time-Anchored Windowing**. Automatically prioritizes extended-hours data based on the US/Eastern clock, bypassing stale API flags.
*   **Self-Hydration**: Automatic loops scan for missing ticker data and force-fetch prices before any deployment. Includes **Bid/Ask Midpoint Fallback** for low-liquidity assets.

---

## 🛠 Troubleshooting & Interaction

### What doesn't get updated?
...

### Why are metrics missing in the Email Dossier?
1.  **Cache Freshness**: The engine now performs a **Just-In-Time (JIT)** refresh if prices are older than 5 minutes. Check the Work Logs for `[INFO] [CACHE] Prices Fresh`.
2.  **Asset Map Error**: Verify the ticker exists in `CPO_MASTER_DATA.json` with the correct name and exchange suffix.

---
*Last Updated: 2026-04-22 — Sovereign Intel V23.86*
