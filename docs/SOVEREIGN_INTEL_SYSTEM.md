# Sovereign Intelligence Engine: Technical Specification (V22.96)

## 1. System Vision
The Sovereign Intelligence Engine (SIE) is a production-grade, autonomous analytical pipeline designed to convert fragmented financial signals into a high-fidelity "Intelligence Dossier." It operates on the principle of **Zero-Cloud Autonomy**, utilizing local statistical modeling to eliminate recurring API costs and data exposure.

```mermaid
graph TD
    A[Yahoo RSS / Web Scrapers] -->|Raw Text| B[PipelineOrchestrator]
    C[Watchlist JSON / master DB] -->|Ticker Context| B
    B --> D{Sovereign NLP Engine}
    D -->|LSA Summarization| E[Dossier Logic]
    D -->|TF-IDF Theme Extraction| E
    D -->|VADER Sentiment| E
    E -->|MIME/Liquid HTML| F[SMTP Dispatch]
    F -->|Gmail/Outlook| G[Sovereign Dossier]
```

## 2. Architectural Pillars

### A. High-Stealth Ingestion & Orchestration
- **Modular Hub**: `email_market_synopsis.py` acts as the central orchestrator, leveraging `live_prices.py` for all real-time price data and `local_nlp.py` for dossier synthesis.
- **Granular 15-Minute Protocol (V22.96)**: Implements a hard **15-minute (900s) asset-level TTL cache**. Both static and dynamic discovery hydration are gated by a per-ticker `timestamp` check in `live_prices.json`, preventing redundant fetches for individual assets even when scripts are run in parallel.
- **Universe Decoupling (V22.96)**: Decouples the **Static Terminal Universe** (107 Root + 29 AI) from the **Dynamic News Discovery** universe. `live_prices.py` remains focused on the hard-coded terminal assets, while the email engine hydrates ad-hoc tickers independently via a direct call to the core fetcher.
- **Session-Aware Pulse (V22.94)**: Uses `get_market_session()` to tag chips with `PM` (Pre), `AH` (After), or `OVN` (Overnight). Integrates high-fidelity BOATS data via `overnightPrice=true` to capture real-time prices during Sunday-night and weekday overnight windows.

### B. Responsive UI Architecture (V22.44)
- **Mobile Lock (< 600px)**: Prioritizes hyper-density and speed. Small typography (9-12px) ensures maximal data visibility on phone screens.
- **Desktop Upsizing (>= 600px)**: Enhances legibility for 4K monitors. Increases section headers to 14-24px and tile values to 20px.

### C. Signal Governance & News Quality
- **NEWS_BLACKLIST**: Automatically purges sensationalist financial commentary (e.g., Jim Cramer / Mad Money) from the synthesis and headline pools.
- **Deduplication Pass**: SHA-256 title-based pruning prevents repetitive news artifacts from biasing the NLP sentiment weights.

### D. Asset Integrity & Data Recovery
- **Self-Hydrating Loops**: Every run performs a "Data-Void" scan. Any discovered symbol missing a price is hydrated in a single transactional batch.
- **Entity Recovery**: Corrects misidentified tickers (e.g., CRCL Circle Internet Financial) in the master database.

## 3. Statistical NLP Pipeline (`engine/local_nlp.py`)
- **LSA (Latent Semantic Analysis)**: Transforms the news corpus into a TDM, performs SVD, and ranks sentences by their importance relative to the dominant semantic concepts.
- **TF-IDF Theme Mapping**: Extracts the top active catalysts for the 48-hour window.
- **VADER Sentiment**: Rule-based scoring optimized for market headlines.

## 4. Engineering Roadmap
- [x] **Desktop/Mobile Parity**: Achieved in V22.44.
- [x] **Granular 15-Minute Protocol**: Production-hardened in V22.96.
- [x] **Session Visibility**: Integrated PM/AH tagging in V22.9.
- [x] **BOATS Overnight Integration**: High-fidelity OVN session detection (V22.94).
- [ ] **Adaptive Lexicons**: Dynamically update VADER scores based on current "Market Vibe".
- [ ] **Entity-Aware Extraction**: Implement `spacy-lite` to identify unmapped M&A targets.

---
*Autonomous System Status: STABLE*
*Last Protocol Update: 2026-04-20 (V22.96)*
