# Sovereign Macro Market Overview

This document serves as the high-level description of the components and indices required to generate the **Sovereign Intelligence Dossier**.

## 1. Global Sovereign Index Pulse
The system tracks high-fidelity session pricing (LIVE, PRE, OVN, AH) for major indices to determine liquidity and volatility.
- **US Equities**: S&P 500 (^GSPC), NASDAQ (^IXIC), DOW 30 (^DJI)
- **Asia / Pacific**: Hang Seng (^HSI), Nikkei 225 (^N225)
- **European Markets**: DAX (^GDAXI), FTSE 100 (^FTSE)
- **Crypto Barometers**: Bitcoin (BTC-USD), Ethereum (ETH-USD), Solana (SOL-USD)

## 2. Fear & Greed Synthesis
The `macro_aggregator.py` evaluates Fear & Greed endpoints:
- Evaluates stock market F&G against crypto F&G to assess risk-on vs. risk-off rotation.
- Injects a "Vibe Status" (e.g., RISK-ON / ACCUMULATING vs RISK-OFF / PROTECTING) guiding the executive narrative.

## 3. High-Alpha Sector Profiles
The engine categorizes raw, high-volatility moves primarily across:
- **Semiconductors / AI**: Tracks supply chain bottlenecks (InP, TSMC CoWoS, custom ELS engines).
- **Macro Drivers**: Employment, Geopolitical conflicts, Energy, Regulatory environments.

## 4. NLP Institutional Narrative
The system synthesizes all the above components into a 3-sentence institutional narrative.
- Utilizing Latent Semantic Analysis (LSA) and VADER Sentiment analysis.
- Summarizing the dominant sector/theme (e.g., "Sector Rotation") alongside current pricing and global news context.
- Maintains a strict 48-hour Time-To-Live (TTL) filter to enforce maximum relevance.
