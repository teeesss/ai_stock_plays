# BetterTwitFix (vxtwitter) Rescue Plan

## Approach
BetterTwitFix is **not** a timeline or search replacement for Nitter (it only resolves single Tweet IDs). It cannot discover tweets across date gaps. However, it is perfect as a **High-Fidelity Rescue Layer**. By querying `api.vxtwitter.com`, we can retrieve robust JSON (full text, media, stats) for specific tweet IDs whenever Nitter scrapes truncate text or fail to load media nodes. 

## Scope
- **In**: Using `api.vxtwitter.com` to repair/enrich known tweet IDs that have malformed data.
- **Out**: Replacing Nitter's search/timeline discovery loop (BetterTwitFix fundamentally lacks this API).

## Action Items
[ ] **Step 1: Rescue Script** — Create `engine/vx_rescue_fetcher.py` with a simple API wrapper for `api.vxtwitter.com/Twitter/status/{id}`.
[ ] **Step 2: Integration Logic** — Add a sub-routine in `x_intel_deep_scraper.py` to route specific tweet IDs to the VX API if their extracted `text` is unusually short, ends in ellipses, or lacks expected media links.
[ ] **Step 3: Missing Media Pass** — Update `image_analyzer` to request the VX API for any posts flagged with `has_media` but a broken image URL.
[ ] **Step 4: Self-Hosting Config** — (Optional) Spin up a local `BetterTwitFix` Docker container if the public `api.vxtwitter.com` rate-limits our fetches.
[ ] **Step 5: Validation** — Feed known broken/truncated tweet IDs through `vx_rescue_fetcher.py` to confirm pristine JSON structures emerge.

## Open Questions
- Do you want this implemented as an "on-the-fly" rescue during the main scrape, or as an async "clean-up pass" that runs alongside the OCR phase?
