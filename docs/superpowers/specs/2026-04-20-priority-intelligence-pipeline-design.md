# Design Spec: Priority Intelligence Pipeline (V23.55)

## 🎯 Goal
Implement a surgical news harvest engine that prioritizes high-alpha semiconductor and photonics intelligence, placing it in a dedicated "Severe Signals" section at the top of the Market Intelligence email.

## 🏗️ Architecture
The system will expand from a passive RSS-only model to an active search-and-harvest model.

### 1. Data Source
- **`priority_tickers.txt`**: A new configuration file containing high-priority tickers (e.g., AMD, NVDA, ALAB, MRVL) and industry keywords (e.g., photonics, CPO).
- **Yahoo Search API**: Use the `query2.finance.yahoo.com/v1/finance/search?q={query}` endpoint for targeted retrieval.

### 2. Logic Flow
- **Stage 1 (Harvest)**: Load `priority_tickers.txt`. For each item, perform a Yahoo search fetching the top 5 most recent stories.
- **Stage 2 (Macro Sync)**: Continue standard RSS fetching for general market vibes.
- **Stage 3 (Scoring & Deduplication)**:
    - **Base Score**: Ticker-specific search results get a baseline of **200 pts**.
    - **Keyword Boost**: +50 pts if the title contains keywords from the priority list.
    - **Cross-Ticker Match**: +100 pts if the story mentions multiple focus tickers (e.g., MRVL + GOOGL).
- **Stage 4 (UI Routing)**:
    - Stories with **Score > 200** are routed to the new **WATCHLIST INTELLIGENCE** section.
    - Others flow into the standard **Macro Intel** feed.

## 🎨 UI Components
- **Section**: `WATCHLIST INTELLIGENCE // SEVERE SIGNALS`
- **Location**: Absolute top of email (below the Pulse grid).
- **Style**: High-density list with ticker badges and context-aware icons (🧠/📡).
- **Limit**: Show the top 10 most relevant priority stories.

## 🛠️ Implementation Details
- **Script**: `engine/email_market_synopsis.py`
- **Utilities**: Update `YahooNewsFetcher` in `engine/news_fetcher.py` if needed (currently supports search).
- **Workflow**: Integrate `priority_harvest` into the `synthesize_dossier` method.

## ✅ Success Criteria
- Ticker-specific news from `priority_tickers.txt` appears at the top of the email.
- Global keyword searches for "photonics" and "CPO" return fresh stories daily.
- No redundant duplication between the priority section and the macro section.
