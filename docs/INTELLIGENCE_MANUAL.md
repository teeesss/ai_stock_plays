# INTELLIGENCE MANUAL: Scoring & Signal Governance

## Overview
The Sovereign Intelligence Engine uses a multi-layered scoring system to distill thousands of headlines into the 15 most relevant high-alpha signals. This manual explains the configuration and logic behind the "Sovereign Score".

---

## 🎯 Scoring Hierarchy

The system calculates a `Sovereign Score` for every headline based on rules defined in `config/macro_config.yaml`.

### 1. Base Weights
- **Feed Weight**: Each news source (e.g., CNBC, Reuters) has a base weight (typically 10-170).
- **Keyword Weight**: Finding a `priority_keyword` adds **+45** points (default).
- **Anchor Weight**: Finding a `anchor_word` (e.g., "WALL ST", "MARKET OVERVIEW") adds **+200** points.

### 2. Multipliers & Bonuses
- **Cluster Multiplier (1.55x)**: If 2+ high-signal terms (e.g., "CPO" + "NVIDIA") appear in the same headline, the score is multiplied by 1.55.
- **Billion-Scale Bonus (+45)**: Regex detection of large financial figures (e.g., "$160B", "50 billion").
- **Institutional Weighting (+50)**: Mentions of Bulge Bracket banks (Goldman, JPMorgan) or elite boutiques.
- **Earnings Boost (+100)**: Headlines containing "EARNINGS" or from the CNBC Earnings feed.

### 3. NLP Sentiment Injection
The `Local NLP Hub` adds an additional layer of intelligence:
- **Macro Bonus (+30)**: High macro relevance.
- **Tech Bonus (+20)**: High technological/sector relevance.
- **Sentiment Shift**: Using FinVADER, keywords like "breakthrough" (+2.5) or "plummet" (-2.5) shift the final ranking.

---

## 🛡️ Signal Governance (Filtering)

To maintain a high signal-to-noise ratio, the system employs aggressive filtering gates.

### 1. Blacklist Protocol
- **Keyword Blacklist**: Any headline containing terms like "Jim Cramer", "Motley Fool", or "Dave Ramsey" is instantly dropped.
- **Domain Blacklist**: Links to forbidden domains (e.g., `fool.com`, `chosunbiz.com`) are discarded.

### 2. Heuristic Gates
- **Interrogative Purge**: Headlines ending in "?" or starting with "Why", "How to", or "Should I" are filtered out (declarative only).
- **Length Gate**: Headlines with fewer than 4 words are ignored to avoid navigation fragments.
- **Video Purge**: Direct links to video-only content are suppressed.

### 3. Freshness Decay
- **Weekday Limit**: 36 hours.
- **Weekend/Stasis Limit**: 60-72 hours.
- **Decay Penalty**: 50% score reduction for articles older than 24 hours (Weekday) or 48 hours (Weekend).
- **Semi Exception**: Core semiconductor trade news (from whitelisted feeds) can persist for up to 14 days without decay.

---

## 🛠️ Configuration: `macro_config.yaml`

All scoring logic is controlled via `config/macro_config.yaml`. This allows for JIT tuning without code changes.

### Key Sections:
- `scoring_rules`: Core weights and multipliers.
- `priority_keywords`: Terms that define the primary investment themes.
- `bonus_keywords`: Variable points for specific high-conviction terms.
- `cluster_terms`: The set of words that trigger the multiplicative boost.
- `forbidden_domains`: Hard-reject list for domains.
- `google_news_whitelist`: Sources allowed through the Google News aggregator.

---

## 📈 Ticker Injection & Flairs

The engine automatically scans headlines for ticker symbols and injects real-time price flairs.
- **Example**: `$AVGO 🟢 +2.0% (AH)`
- **Logic**: It uses a `ticker_name_map.json` to bridge company names (e.g., "Broadcom") to tickers (`AVGO`).
- **Session Awareness**: Flairs automatically reflect the active session (PRE, AH, OVN, or LIVE).
