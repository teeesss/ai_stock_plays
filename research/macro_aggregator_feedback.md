Excellent codebase — this is already a highly sophisticated, production-grade news aggregator with smart hardening, velocity tracking, source diversity, freshness decay, and institutional weighting. It's clean, well-commented, and purpose-built for your "GIGACPO Cockpit" use case.
Here are targeted improvements across keywords/words, stocks/tickers, scoring system, feeds/filtering, and bonus points section.
1. Scoring System – Already Great, Make It More User-Friendly
Yes, you already have a flexible scoring system. Users can tweak it easily by editing lists or adding conditions in score_headline().
Recommended Improvements (add these to __init__):
Python# V27: Weighted Bonus System - Easy for users to customize
        self.bonus_keywords = {
            # High-signal photonics / packaging terms (extra points even if in priority_keywords)
            "CPO": 120,
            "CO-PACKAGED OPTICS": 150,
            "SILICON PHOTONICS": 130,
            "1.6T": 110,
            "3.2T": 110,
            "800G": 80,
            "COUPE": 100,           # TSMC CoWoS + CPO context
            "HETEROGENEOUS INTEGRATION": 90,
            "OPTICAL ENGINE": 95,

            # Supply chain / equipment
            "ASML": 80,
            "TSMC": 75,
            "COHERENT": 70,
            "LUMENTUM": 70,

            # Macro + AI scale
            "BLACKWELL": 60,
            "RUBIN": 80,
            "$BILLION": 40,   # or use regex below
        }

        # Tiered multipliers (optional)
        self.score_multipliers = {
            "earnings": 1.5,
            "photonics_cluster": 1.8,   # if multiple photonics terms
        }
Updated score_headline() (key changes):
Pythondef score_headline(self, title, source_name):
        t_upper = title.upper()
        if any(bl in t_upper for bl in self.blacklist):
            return -1000

        score = self.feeds.get(source_name, {}).get("weight", 10)

        # Standard keyword bonus
        for kw in self.priority_keywords:
            if kw in t_upper:
                score += 50

        # BONUS SECTION - Custom points
        for kw, points in self.bonus_keywords.items():
            if kw in t_upper:
                score += points

        # Anchor bonuses (keep your +200)
        anchor_words = ["MARKET OVERVIEW", "WALL ST", ...]
        for aw in anchor_words:
            if aw in t_upper:
                score += 200

        # Regex for big money / scale
        if re.search(r'\$\s?\d+(\.\d+)?\s?(B|BN|BILLION)', t_upper) or \
           re.search(r'\d+(\.\d+)?\s?(B|BN|BILLION)', t_upper):
            score += 45

        # Cluster bonus example: multiple high-signal terms
        photonics_hits = sum(1 for term in ["CPO", "PHOTONICS", "1.6T", "OPTICAL ENGINE"] if term in t_upper)
        if photonics_hits >= 2:
            score *= 1.4   # or += 80

        return round(score, 1)
This gives you a clean, user-editable bonus section separate from the main list.
2. Expanded Priority Keywords (Merge Your Original + My Previous + New Terms)
Replace your priority_keywords with this expanded version:
Pythonself.priority_keywords = [
            # Core + AI
            "SEMICONDUCTOR", "SEMI", "CHIP", "CHIPS", "WAFER", "SILICON", "NVIDIA", "BLACKWELL", "RUBIN",
            "GPU", "HBM", "HBM3", "HBM4", "AI REVENUE", "SUPPLY CHAIN",

            # Photonics & Optics
            "PHOTONICS", "SILICON PHOTONICS", "SIPH", "CPO", "CO-PACKAGED OPTICS", "COPACKAGED",
            "LPO", "LINEAR DRIVE", "OPTICAL ENGINE", "PIC", "PHOTONIC INTEGRATED CIRCUIT",
            "VCSEL", "LASER", "CW LASER", "EML", "MODULATOR", "MZM", "MRM", "EAM",

            # Transceivers
            "TRANSCEIVER", "400G", "800G", "1.6T", "1600G", "3.2T", "3200G", "OSFP", "QSFP",

            # Packaging & Manufacturing
            "ADVANCED PACKAGING", "OSAT", "INTERPOSER", "COUPE", "CO-WOS", "HETEROGENEOUS INTEGRATION",
            "FOU", "FAN OUT", "FOUNDry", "TSMC",

            # Materials / Equipment
            "EUV", "ASML", "PHOTORESIST", "LITHOGRAPHY", "INDIUM PHOSPHIDE", "INP", "GALLIUM",

            # Market signals (keep yours)
            "MARKET OVERVIEW", "WALL ST", "CLOSING BELL", "EARNINGS", "REVENUE", "GUIDANCE", "IPO",
            "CRUDE", "OIL", "GEOPOLITICAL", "DEFENSE",
        ]
3. Improved priority_tickers (2026-Relevant)
Pythonself.priority_tickers = [
            # Big AI / Semi
            "NVDA", "AMD", "AVGO", "TSM", "INTC", "MU", "AMAT", "LRCX", "KLAC",
            # Photonics / Optics leaders
            "LITE", "COHR", "FN", "POET", "AAOI", "LASR", "IPGP", "MKSI",
            # Others strong in supply chain
            "MRVL", "ALAB", "ARM", "CRUS", "SWKS", "QRVO", "AEHR", "FORM",
            "HIVE", "RMBS", "PII"  # keep yours
        ]
4. Feed & Source Improvements
Your current feeds are solid. Suggested additions (high-signal for your niche):

Semiconductor Engineering: https://semiengineering.com/feed/
Semiconductor Today: https://www.semiconductor-today.com/rss.shtml
SemiWiki: Check their RSS
LightCounting or Yole (if available)
More Google News targeted:
q=co-packaged+optics+OR+silicon+photonics+when:1d
q=CPO+OR+1.6T+transceiver+when:1d


Add a "relevance_multiplier": 1.8 in feeds dict for photonics-heavy sources.
Forbidden domains — consider adding more low-value ones if you see noise.
5. Other Polish Suggestions

Velocity Pulse: Add cluster detection (e.g., "CPO + NVIDIA" in same window = extra velocity).
is_article_safe(): Add positive tech anchors to reduce over-filtering on good niche articles.
Cache & DB: Consider compressing or rotating old velocity data.
Config File: Move all lists (priority_keywords, bonus_keywords, feeds, tickers) to a config.yaml for non-code edits.

Would you like me to output the full updated __init__ + score_headline with all these changes integrated, or focus on one area (e.g., just the bonus system + new keywords)?
This setup will catch way more high-alpha photonics/packaging articles while keeping noise low. Great work on the foundation!
