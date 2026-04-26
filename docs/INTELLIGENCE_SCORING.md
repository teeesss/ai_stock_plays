# Intelligence Scoring & Discovery Mandates // SIE V28

## 1. The "Intel Significance" Score
The Sovereign Intelligence Engine (V28) utilizes a multi-layered weighted scoring heuristic to extract institutional-grade alpha from raw news data.

### 1.1 Config-First Base Weights
All weights are defined in `config/macro_config.yaml`.
- **Institutional Bulge Bracket**: Reuters (160), CNBC (145), FT (155), Bloomberg (BLOCKED/SCRAPE).
- **Semiconductor Specialized**: SemiEngineering (160), SemiToday (155), SemiWiki (155).
- **Macro Anchor (+200)**: Global recaps and market summaries are forced to the hierarchy leader position.

---

## 2. FinVADER NLP Architecture (V28)
V28 transitioned to **Statistical Financial NLP** using the FinVADER integration.

### 2.1 Lexicon Injection
- **SentiBignomics & Henry**: High-fidelity financial dictionaries are injected into the VADER analyzer at runtime.
- **YAML Lexicon Overrides**: Scoring rules can be mathematically dictated via the `vader_financial_lexicon` block in the config file (e.g., `breakthrough: 2.5`).

### 2.2 Nuclear Hard Gates (Rejection Logic)
To maintain a high signal-to-noise ratio, SIE V28 employs **Nuclear Gates**:
- **Litigation / Lawsuit Gate**: Keywords like "class action", "investor counsel", "lawsuit", and "settles with" trigger an immediate **-200.0** penalty, vaporizing the item.
- **Consumer / Social Fluff Gate**: News about "teenagers", "kids", "lifestyle", or "vacation" is purged to preserve institutional focus.

---

## 3. Advanced Multipliers
- **Priority Clusters (1.55x)**: Headlines containing 2+ high-signal terms (e.g., "NVIDIA" + "CPO") receive a massive multiplier.
- **Billion-Scale Detection (+45)**: Regex-based detection of $100B+, "50 billion", or "100BN" figures grants a high-stakes bonus.
- **Institutional Hierarchy (+50)**: Mentions of Bulge Bracket banks (Goldman, Morgan Stanley) or elite Hedge Funds (Citadel, Millennium) receive a signal boost.

---

## 4. Freshness Gates (V28 Temporal Overhaul)
SIE V28 enforces a **Dual-Tier Freshness Protocol**:

### 4.1 Tier 1: Macro News
- **Hard Gate**: 36 hours (Weekday) / 60 hours (Weekend Stasis).
- **Decay**: 50% penalty after 24 hours.

### 4.2 Tier 2: Semi Trade News (Top Hierarchy)
- **14-Day Lookback**: Specialized semiconductor trade sources (`is_semi: true`) are allowed to go back **336 hours**.
- **Decay Exemption**: Trade news is exempt from score decay within the 14-day window to ensure weekly technical catalysts are preserved.

---

## 5. Signal Integrity & Relevance Floor
- **Relevance Floor (22.0)**: Macro articles scoring below this threshold are discarded.
- **Specialized Floor (-50.0)**: Trade news has a lower floor to ensure "Week In Review" and "Suppliers" updates are not accidentally purged by the NLP aggregator.

---

## 6. Source Diversity & Rotation
- **Max Per Source**: 15 articles.
- **Article Rotation Engine**: The `sent_news_history.json` ledger tracks previously dispatched URLs for 24 hours to ensure the morning/afternoon dossiers remain fresh.

---
*Document Version: 28.00 // Last Hardening: 2026-04-26*
