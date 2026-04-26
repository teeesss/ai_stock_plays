# BetterTwitFix (vxtwitter) Rescue Plan

## Approach
BetterTwitFix is **not** a timeline or search replacement for Nitter (it only resolves single Tweet IDs). It cannot discover tweets across date gaps. However, it is perfect as a **High-Fidelity Rescue Layer**. By querying `api.vxtwitter.com`, we can retrieve robust JSON (full text, media, stats) for specific tweet IDs whenever Nitter scrapes truncate text or fail to load media nodes.

## Scope
- **In**: Using `xtwitter.com` to repair/enrich known tweet IDs that have malformed data.
- **Out**: Replacing Nitter's search/timeline discovery loop (BetterTwitFix fundamentally lacks this API).

## Action Items
[x] **Step 1: Rescue Script** — Created `engine/vx_rescue_fetcher.py`.
[x] **Step 2: Integration Logic** — Added to `x_intel_deep_scraper.py` (Text-based trigger).
[x] **Step 3: Missing Media Pass** — Added to `download_images` (Failed-download trigger).
[x] **Step 4: Self-Hosting Config** — Skipped (Public API stable).
[x] **Step 5: Validation** — Verified via `terminal.py` Option 11.

## Status: COMPLETE
BetterTwitFix is now a mandatory high-fidelity fallback for all scraping entry points.
