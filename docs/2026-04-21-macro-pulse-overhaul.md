# Macro Pulse Overhaul (2026-04-21)

## V23.60 - V23.76: Institutional Intelligence Narrative

The Macro Pulse and Sovereign Intelligence Engine underwent a massive hardening phase to transition from a list of disjointed headlines into a cohesive, NLP-driven institutional overview.

### 1. Extractive Summarization (LSA)
The system no longer just concatenates the top headlines. It uses Latent Semantic Analysis (LSA) and TF-IDF scoring to identify the core thematic sentences from the top 10 RSS articles, cross-referencing descriptions and full text.
The `synthesize_market_narrative` constructs a dense 3-sentence institutional paragraph:
- **Lead Anchor:** Focuses on the top-priority macro event.
- **Thematic Bridge:** Uses LSA filtering to avoid redundancy, merging context across articles.
- **Regime Closure:** Synthesizes the overall market fear/greed into a "Vibe" (e.g., RISK-ON).

### 2. Sentence Deduplication
To handle duplicate syndications (e.g., CNBC and Yahoo reporting the same story with identical wording), a strict string-matching loop ensures that unique points are preserved without "stuttering."

### 3. Intelligence Hygiene
- **48-Hour TTL:** Any RSS article older than 48 hours is instantly discarded. This prevents stale news (e.g., 2024 historical articles) from polluting live market pulse data.
- **Strict Blacklists:** Sites and authors that produce low-signal "noise" are regex-filtered entirely from the NLP extraction.
- **Regex Ticker Detection:** Using `\b` boundaries, the scraper perfectly distinguishes between "$ARM" and "arming", preventing hallucinated volatility tags inline.

### 5. Market Pulse Index Futures (V23.86)
Indices now support dynamic ticker mapping. If the system is in `PRE`, `AH`, or `OVN` session, the `S&P 500`, `NASDAQ`, and `DOW` tiles automatically switch from cash tickers (`^GSPC`) to front-month futures (`ES=F`, `NQ=F`, `YM=F`). This provides 24/7 price action in the market pulse strip.

### 6. Work Log Transparency
To ensure diagnostic visibility during automated runs, the aggregation engine explicitly logs:
- **Cache TTL**: Seconds remaining for Macro News and Live Prices.
- **NLP Relevance**: The top-ranked "Lead Intelligence" headline being utilized for the executive summary.
- **Coverage Audit**: Total count of master vs. custom tickers ingested.
