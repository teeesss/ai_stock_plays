# Engine Architecture

## The GIGACPO Intelligence Ecosystem

The intelligence architecture is split into synchronized sub-engines that handle isolation, ingestion, analysis, and dispatch. By decoupling these elements, the pipeline achieves resilience and stateless processing.

### 1. `dependency_mgr.py` (The Guardian)
* **Goal**: Guarantee zero-friction deployment.
* **Architecture**: Uses `importlib.util` and `os.execv` to dynamically intercept missing libraries, spawn `pip` processes bound to the exact calling Python interpreter, and automatically restart the script seamlessly.

### 2. `live_prices.py` (The Pulse)
* **Goal**: Provide low-latency, session-aware pricing across multi-market assets without hitting API limits.
* **Architecture**: Intercepts Yahoo Finance v7 endpoints using HTTP requests (`cffi_requests`).
* **Protocol (V23.86)**: Implements **Time-Anchored Windowing** to force-prioritize `preMarketPrice` or `postMarketPrice` during specific clock hours, bypassing stale Yahoo state reporting. Includes **Bid/Ask Midpoint Fallback** for low-liquidity extended sessions.

### 3. `macro_aggregator.py`
* **Goal**: Harvest global headlines, filter out sensationalist noise, and rank by alpha-generating priorities.
* **Architecture**: Pulls multi-feed RSS data, assigns Base Impact scores (+50 for UI/Geopolitics, +20 for Corporate), and boosts AI/SiPh-specific keywords (e.g. Photonics +50). Prunes data > 48 hours old.

### 4. `local_nlp.py` (The Synthesizer)
* **Goal**: Turn raw text extraction into cohesive institutional narratives.
* **Architecture**: Fully offline. Utilizes NLTK, VADER Sentiment, and LSA algorithms. Deduplicates intersecting stories and produces density-first overviews mimicking tier-1 intelligence desks.

### 5. `email_market_synopsis.py` (The Orchestrator)
* **Goal**: Render the final payload.
* **Architecture**: Merges sentiment metrics, live prices, macro text, and watchlist tracking into a single HTML stream. 
* **Hardening (V23.86)**: Enforces **Atomic Session Overrides** (paired price/pct updates) and **Work Log Transparency** (verbose cache/NLP diagnostics). Minifies document to <102KB for Gmail compliance.
