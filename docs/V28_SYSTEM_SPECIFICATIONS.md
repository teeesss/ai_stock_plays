# Sovereign Intelligence Engine (SIE) // V28 System Specifications

## 1. Core Runtime Environment
- **Runtime**: Python 3.11+ / Node.js 20+
- **Primary Dependencies**:
  - `curl_cffi` (Impersonation)
  - `beautifulsoup4` (Extraction)
  - `vaderSentiment` / `finvader` (Statistical NLP)
  - `pandas` / `numpy` (Quant Analysis)
  - `sumy` (LSA Synthesis)

## 2. Stealth & Security Profile
- **Global User-Agent**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/160.0.8827.0 Safari/537.36`
- **TLS Fingerprint**: Chrome 160 (Identity Protocol 2026)
- **Session Persistence**: `engine/stealth_session.json` (Automated recovery)
- **Rate Limit Resilience**: Multi-gateway pool (OpenGraph + RSS)

## 3. Data Integrity Benchmarks
- **Pricing Fidelity**: Universal Time-Normalized (NYSE/NASDAQ authority)
- **Article Rotation**: 24-hour deduplication via `database/sent_news_history.json`
- **UTF-8 Mandate**: All artifacts must pass mandatory UTF-8 validation checks
- **Database Architecture**: Flat JSON (Atomic Save-then-Swap protocol)

## 4. Hardware/Infrastructure Mandates
- **Memory Footprint**: <512MB RAM during peak aggregation
- **Network Bound**: Sequential 200ms jitter between domain-specific fetches
- **Disk I/O**: Minimized via high-frequency cache (15m TTL)

## 5. UI/UX Design Tokens
- **Font Stack**: Inter, Roboto, sans-serif
- **Primary Palette**:
  - Institutional Blue: `#38BDF8`
  - Growth Green: `#4ADE80`
  - Alert Orange: `#F59E0B`
- **Layout Mandate**: Single-line ticker rows (White-space: nowrap)
- **Responsiveness**: Fluid-scaling typography for Desktop (600px+) vs Mobile

---
*V28 System Specs // Last Hardening: 2026-04-26*
