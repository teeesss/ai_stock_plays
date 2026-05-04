# V28: Local Intelligence Synthesizer
import re

# V28: Hierarchy Leader Error Monitoring
try:
    from error_monitor import init_error_monitor
except ImportError:
    from engine.error_monitor import init_error_monitor
init_error_monitor()
from collections import Counter

try:
    from ticker_utils import SEMI_SOURCES
except ImportError:
    from engine.ticker_utils import SEMI_SOURCES

import nltk

try:
    from pathlib import Path

    import yaml
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.summarizers.lsa import LsaSummarizer
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    try:
        from finvader import Merge, lexicon1, lexicon2

        HAS_FINVADER = True
    except ImportError:
        HAS_FINVADER = False
except ImportError:
    pass


class LocalIntelligenceSynthesizer:
    def __init__(self):
        # V30.0: Narrative Engine Vocabulary
        self.PULSE_OPENERS = [
            "Market dynamics are shifting toward {vibe} as {theme} takes center stage.",
            "Equities are carving out a {vibe} posture, driven primarily by {theme} catalysts.",
            "Institutional appetite remains {vibe}, with focus centering on the {theme} complex.",
            "The broad market is navigating a {vibe} session, as {theme} becomes the primary narrative anchor.",
        ]
        self.CONNECTORS = [
            "In parallel, {insight}.",
            "This development coincides with {insight}.",
            "Furthermore, {insight}.",
            "Meanwhile, {insight}.",
        ]
        self.OUTLOOKS = [
            "Looking ahead, the technical setup remains anchored by {sentiment} sentiment.",
            "The forward outlook is strictly contingent on {sentiment} developments.",
            "Traders are monitoring {sentiment} signals for the next high-alpha opportunity.",
        ]

        # V30.0: Theme & Catalyst Blacklist
        self.THEME_BLACKLIST = [
            "SESSION PERFORMANCE",
            "500",
            "INDEX",
            "MARKET",
            "STOCK",
            "UPDATE",
            "TODAY",
            "DAILY",
            "RECAP",
            "SUMMARY",
            "DESK",
            "PULSE",
            "NEWS",
            "EDWARD JONES",
            "CNBC",
            "YAHOO",
            "FINANCE",
            "NEWS.GOOGLE",
            "GOOGLE NEWS",
            "PERFORMANCE",
            "DISCLOSURE",
            "IMPORTANT",
            "CHART",
            "IMAGE",
            "VIDEO",
            "SESSION",
            "MORNING",
            "EVENING",
            "AFTERNOON",
            "WEEKEND",
            "LATEST",
            "NBSP",
            "HTML",
            "URL",
            "HTTPS",
            "HTTP",
        ]

        try:
            self.analyzer = SentimentIntensityAnalyzer()
            self.is_active = True

            # V28: Inject FinVADER Lexicons
            if HAS_FINVADER and not getattr(
                LocalIntelligenceSynthesizer, "_LEXICON_INJECTED", False
            ):
                # Merge SentiBignomics and Henry lexicons
                fin_lexicon = Merge(lexicon1(), lexicon2())
                self.analyzer.lexicon.update(fin_lexicon)
                print(
                    f"[INFO] [NLP] FinVADER Financial Lexicons Injected ({len(fin_lexicon)} terms)"
                )
                LocalIntelligenceSynthesizer._LEXICON_INJECTED = True

            # V28: Inject Config-First Lexicon Overrides
            try:
                root_path = Path(__file__).parent.parent
                cfg_path = root_path / "config" / "macro_config.yaml"
                if cfg_path.exists():
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f) or {}
                        custom_lexicon = cfg.get("scoring_rules", {}).get(
                            "vader_financial_lexicon", {}
                        )
                        if custom_lexicon:
                            self.analyzer.lexicon.update(custom_lexicon)
            except Exception as e:
                print(f"[NLP CONFIG ERR] Failed to load custom lexicon: {e}")

            # Base stopwords
            self.base_stops = [
                "stock",
                "stocks",
                "market",
                "need",
                "know",
                "buy",
                "investor",
                "investors",
                "today",
                "company",
                "shares",
                "wall",
                "street",
                "year",
                "announced",
                "report",
                "results",
                "quarter",
                "q1",
                "q2",
                "q3",
                "q4",
            ]

            # V28: Dynamic Relevance Floor
            self.relevance_floor = 22.0
            try:
                root_path = Path(__file__).parent.parent
                cfg_path = root_path / "config" / "macro_config.yaml"
                if cfg_path.exists():
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f) or {}
                        self.relevance_floor = cfg.get("scoring_rules", {}).get(
                            "relevance_floor", 22.0
                        )
                        if not getattr(LocalIntelligenceSynthesizer, "_LEXICON_INJECTED", False):
                            print(
                                f"[INFO] [NLP] Relevance Floor initialized: {self.relevance_floor}"
                            )
            except:
                pass
        except Exception as e:
            print(f"[NLP INIT ERR] {e}")
            self.is_active = False

    def update_vibe_lexicon(self, sentiment_data: dict):
        """Bias VADER lexicon based on Market Fear & Greed levels."""
        if not self.is_active:
            return

        m_val = sentiment_data.get("market", {}).get("value", 50)
        c_val = sentiment_data.get("crypto", {}).get("value", 50)
        vibe = (m_val + c_val) / 2

        # Inject "Market Vibe" biased tokens
        if vibe < 30:  # Extreme Fear
            self.analyzer.lexicon.update(
                {
                    "oversold": 2.5,
                    "support": 1.5,
                    "capitulation": -0.5,
                    "opportunity": 2.0,
                }
            )
        elif vibe > 70:  # Extreme Greed
            self.analyzer.lexicon.update(
                {
                    "frothy": -1.5,
                    "bubble": -2.0,
                    "overextended": -1.5,
                    "exhausted": -1.0,
                }
            )
        else:
            # Reset / Neutral bias
            self.analyzer.lexicon.pop("oversold", None)
            self.analyzer.lexicon.pop("frothy", None)

    def discover_entities(self, text: str) -> list:
        """Lightweight Named Entity Recognition to find unmapped organizations."""
        if not self.is_active or not text:
            return []
        try:
            tokens = nltk.word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            chunks = nltk.ne_chunk(pos_tags)
            entities = []
            for chunk in chunks:
                if hasattr(chunk, "label") and chunk.label() == "ORGANIZATION":
                    name = " ".join([c[0] for c in chunk])
                    if (
                        len(name) > 2
                        and name.lower() not in self.base_stops
                        and name.upper() not in self.THEME_BLACKLIST
                    ):
                        entities.append(name)
            return list(set(entities))
        except:
            return []

    def synthesize_macro_overview(
        self, articles: list, sentences_count=5, group_paragraphs=False
    ) -> list:
        if not self.is_active or not articles:
            return []

        all_text = ""
        seen = set()
        for a in articles:
            title = a.get("title", "").strip()
            summary = a.get("summary", "").strip()

            # Token Efficiency: Skip summary if it's just the title or too generic
            if summary.lower() in title.lower() or "yahoo" in summary.lower():
                content = title
            else:
                content = f"{title}. {summary}"

            if content not in seen:
                seen.add(content)
                all_text += content + ". "

        if len(all_text.strip()) < 50:
            return [a.get("title") for a in articles[:3]]

        try:
            parser = PlaintextParser.from_string(all_text, Tokenizer("english"))
            # V22.55: Dynamic sentence count adjustment to prevent LSA failure
            s_count = min(sentences_count, len(parser.document.sentences))
            if s_count < 1:
                return articles[:3] if isinstance(articles, list) else []  # Fallback to top news

            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, sentences_count=s_count)
            s_list = [str(s) for s in summary]

            # NLP Fallback: if summarizer returns empty but text exists, join first few sentences
            if not s_list and all_text:
                sentences = re.split(r"\. |\? |\! ", all_text)
                s_list = [s.strip() for s in sentences if len(s.strip()) > 10][:5]

            if group_paragraphs:
                # Group every ~3-4 sentences into a structured topic
                paras = []
                transitions = [
                    "Intelligence Brief",
                    "Catalyst Dynamics",
                    "Structural Shifts",
                    "Sector Tailwinds",
                ]
                for i in range(0, len(s_list), 4):
                    chunk = s_list[i : i + 4]
                    group = {
                        "transition": transitions[len(paras) % len(transitions)],
                        "items": [],
                    }
                    for s in chunk:
                        s_str = s.strip()
                        if not s_str.endswith((".", "!", "?")):
                            s_str += "."

                        link = "#"
                        prefix = s_str[:30].lower()
                        for a in articles:
                            if (
                                prefix in a.get("title", "").lower()
                                or prefix in a.get("summary", "").lower()
                            ):
                                link = a.get("link", "#")
                                break

                        group["items"].append({"text": s_str, "link": link})
                    paras.append(group)
                return paras

            return s_list
        except Exception as e:
            print(f"[NLP ERR] {e}")
            return []

    def synthesize_market_narrative(
        self, articles: list, vibe: str, scraped_lead: str = None
    ) -> tuple:
        """Constructs a dense, cohesive institutional paragraph. Returns (narrative, used_links)."""
        used_links = set()

        # 1. Determine Primary Anchor
        if scraped_lead and len(scraped_lead) > 50:
            lead_para = scraped_lead.strip()
            # If we have a scraped lead, we don't have its specific link here,
            # but we can try to filter out articles that overlap too much.
            anchor_words = set(re.findall(r"\b\w{4,}\b", lead_para.lower()))
        elif articles:
            anchor = articles[0]
            used_links.add(anchor.get("link"))

            # V29.0: Deep Content Priority
            deep = anchor.get("deep_content", "").strip()
            if deep and len(deep) > 100:
                lead_para = deep[:1200]  # Use first 1200 chars for context
            else:
                lead_para = anchor.get("summary", "").strip()

            if len(lead_para) < 40:
                lead_para = anchor.get("raw_title", "").strip()
            anchor_words = set(re.findall(r"\b\w{4,}\b", lead_para.lower()))
        else:
            return (
                f"The market maintains a {vibe} posture. No primary catalysts identified.",
                set(),
            )

        if not lead_para.endswith((".", "!", "?")):
            lead_para += "."

        # 2. Extract Top Themes
        themes = self.get_top_themes(articles, top_n=2)
        top_theme = themes[0] if themes else "Sector Rotation"
        if top_theme.upper() == "AI":
            top_theme = "AI"
        else:
            top_theme = top_theme.title()

        # 3. Extract Secondary Insights (avoiding stutter)
        dense_points_with_meta = self.synthesize_macro_overview_with_meta(
            articles, sentences_count=1
        )

        dense_text = ""
        for pt, link in dense_points_with_meta:
            if not pt:
                continue

            # Stutter check against the lead
            pt_words = set(re.findall(r"\b\w{4,}\b", pt.lower()))
            overlap = len(pt_words & anchor_words) / (len(pt_words) + 1)
            if overlap > 0.4:
                continue  # Tighter threshold for scraped leads

            dense_text = pt
            if link:
                used_links.add(link)
            break

        # 4. Final Institutional Construction (V28: Priority Ordering)
        # Return structured data for the orchestrator to handle the "Intelligence Strip" UI
        points = []

        def clean_and_split(text):
            if not text:
                return []
            # V28.8: Hardened Greedy Splitter
            # Splits on . ! ? followed by space, BUT ignores common institutional abbreviations
            # and prevents splitting if the next word is lowercase.
            raw_sents = re.split(r"(?<=[.!?])\s+", text.strip())
            merged = []
            for s in raw_sents:
                s = s.strip()
                if not s:
                    continue
                # If this sentence starts with lowercase or the previous sentence ended in an abbreviation, merge
                abbreviations = [
                    "univ",
                    "university",
                    "inc",
                    "corp",
                    "tech",
                    "technology",
                    "inst",
                    "institute",
                    "assn",
                    "dept",
                    "ltd",
                    "lab",
                    "laboratory",
                    "co",
                    "corp",
                    "incorporated",
                    "res",
                    "research",
                    "st",
                    "ave",
                ]
                # Check for abbreviation suffix before the period
                last_word = merged[-1].split()[-1].lower().rstrip(".!?,") if merged else ""
                if merged and (s[0].islower() or last_word in abbreviations):
                    merged[-1] = f"{merged[-1]} {s}"
                else:
                    merged.append(s)
            return merged

        if lead_para:
            points.extend(clean_and_split(lead_para))

        if dense_text:
            points.extend(clean_and_split(dense_text))

        # V30.0: Narrative Engine V2 (Human-Grade Synthesis)
        # Attempt to build a template-driven composite narrative for 90%+ human feel
        try:
            narrative = self._build_human_grade_narrative(
                vibe, lead_para, dense_text, top_theme, articles
            )
            return {"vibe": vibe, "focal_point": top_theme, "points": [narrative]}, used_links
        except Exception as e:
            print(f"[NLP] Narrative V2 failed, falling back to extractive: {e}")
            return {"vibe": vibe, "focal_point": top_theme, "points": points}, used_links

    def _build_human_grade_narrative(self, vibe, lead, dense, theme, articles) -> str:
        """Assembles a professional market narrative using institutional templates."""
        import random

        # 1. Pulse Opener
        vibe_adj = "bullish" if vibe.lower() in ["bullish", "greed", "risk-on"] else "cautious"
        if vibe.lower() in ["bearish", "fear", "risk-off"]:
            vibe_adj = "defensive"

        # Theme cleanup (avoid numeric or blacklisted themes)
        # V30.2: Aggressive dot removal to prevent Gmail auto-link corruption
        clean_theme = theme.upper().replace(".", " ").replace("NBSP", "").strip()
        if clean_theme.isdigit() or len(clean_theme) < 3 or clean_theme in self.THEME_BLACKLIST:
            clean_theme = "MACRO"

        opener = random.choice(self.PULSE_OPENERS).format(vibe=vibe_adj, theme=clean_theme)

        # Catalyst (Lead)
        # V30.3: Hardened split to avoid breaking on decimals (e.g. 0.5%)
        sentences = re.split(r"(?<!\d)\.(?!\d)|(?<=\D)\.(?=\d)|(?<=\d)\.(?=\D)", lead)
        catalyst = sentences[0].strip() if sentences else "market catalysts remain fluid"

        # Hardened Blacklist check (substring match)
        is_blacklisted = any(bad in catalyst.upper() for bad in self.THEME_BLACKLIST)
        if is_blacklisted:
            if len(sentences) > 1:
                catalyst = sentences[1].strip()
            else:
                catalyst = "market catalysts remain fluid"

        # Double-check cleaned catalyst & secondary catch-all
        if (
            any(bad in catalyst.upper() for bad in self.THEME_BLACKLIST)
            or "SESSION PERFORMANCE" in catalyst.upper()
        ):
            catalyst = "market catalysts remain fluid"

        if len(catalyst) < 30 and len(sentences) > 1:
            catalyst = sentences[0] + ". " + sentences[1]

        # V30.2: Mandatory Sanitization (Strip NBSP and dots NOT in numbers)
        catalyst = catalyst.replace("NBSP", "")
        catalyst = re.sub(r"(?<!\d)\.(?!\d)", " ", catalyst)  # Replace periods not in decimals
        catalyst = re.sub(r"\s+", " ", catalyst).strip()

        # Grammar Guard: "The primary lead stems from The..." -> "The primary lead stems from the..."
        if catalyst.lower().startswith("the "):
            catalyst = catalyst[4:]  # Remove "The " prefix

        catalyst_sent = f"The primary lead stems from {catalyst}."

        # 3. Secondary Insight (Dense)
        insight = "steady flows across major sectors"
        if dense:
            # Strip common fluff from start
            insight = re.sub(
                r"^(Meanwhile|Furthermore|In parallel|Additionally),?\s*", "", dense, flags=re.I
            )
            # Grammar Guard for second sentence
            if insight.lower().startswith("the "):
                insight = insight[4:]

            # V30.2: Strip dots and NBSP from insight as well
            insight = insight.replace("NBSP", "")
            insight = re.sub(r"(?<!\d)\.(?!\d)", " ", insight)
            insight = insight.strip()

        connector = random.choice(self.CONNECTORS).format(insight=insight)

        # 4. Outlook
        sentiment_vibe = "stabilizing" if vibe_adj == "bullish" else "shifting"
        outlook = random.choice(self.OUTLOOKS).format(sentiment=sentiment_vibe)

        # Assemble
        full = f"{opener} {catalyst_sent} {connector} {outlook}"

        # Final cleanup
        full = full.replace("NBSP", "").replace("nbsp", "").replace("  ", " ").strip()
        if not full.endswith("."):
            full += "."
        return full

    def synthesize_macro_overview_with_meta(self, articles: list, sentences_count=2) -> list:
        """Helper to get sentences with their source links."""
        try:
            from sumy.nlp.tokenizers import Tokenizer
            from sumy.parsers.plaintext import PlaintextParser
            from sumy.summarizers.lsa import LsaSummarizer

            # Map sentences back to articles
            doc_text = ""
            link_map = {}
            for a in articles:
                text = a.get("summary", a.get("raw_title", ""))
                doc_text += text + " "
                # Very crude mapping
                for sentence in re.split(r"(?<=[.!?])\s+", text):
                    if len(sentence) > 20:
                        link_map[sentence.strip()] = a.get("link")

            parser = PlaintextParser.from_string(doc_text, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, sentences_count)

            results = []
            for s in summary:
                s_text = str(s).strip()
                results.append((s_text, link_map.get(s_text)))
            return results
        except:
            return [
                (a.get("summary", a.get("raw_title", "")), a.get("link"))
                for a in articles[:sentences_count]
            ]

    def get_top_themes(self, articles: list, top_n=5) -> list:
        if not self.is_active or not articles:
            return []

        all_text_list = []
        seen = set()
        for a in articles:
            t = (a.get("title", "") + ". " + a.get("summary", "")).strip()
            if t not in seen:
                seen.add(t)
                all_text_list.append(t)

        if not all_text_list:
            return []
        all_text = " ".join(all_text_list)

        try:
            # Dynamic Stopwords: Identify "noise" specific to this batch (appears in >40% of docs)
            words = re.findall(r"\b\w{4,}\b", all_text.lower())
            doc_counts = Counter()
            for text in all_text_list:
                doc_words = set(re.findall(r"\b\w{4,}\b", text.lower()))
                for w in doc_words:
                    doc_counts[w] += 1

            thresh = len(all_text_list) * 0.4
            dynamic_stops = [w for w, count in doc_counts.items() if count > thresh and count > 2]

            custom_stops = (
                list(TfidfVectorizer(stop_words="english").get_stop_words())
                + self.base_stops
                + dynamic_stops
            )
            vectorizer = TfidfVectorizer(
                stop_words=custom_stops, max_features=40, ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer.fit_transform([all_text])
            feature_names = vectorizer.get_feature_names_out()
            top_keywords = sorted(
                zip(feature_names, tfidf_matrix.sum(axis=0).flat),
                key=lambda x: x[1],
                reverse=True,
            )[:top_n]

            results = []
            for kw, _ in top_keywords:
                clean_kw = kw.title().replace(".", " ").strip()
                if clean_kw.upper() not in self.THEME_BLACKLIST:
                    results.append(clean_kw)

            # NER Integration: Inject a top discovered entity if relevant
            entities = self.discover_entities(all_text)
            if entities:
                results.insert(1, f"Focus: {entities[0]}")

            return results[:top_n]
        except Exception as e:
            print(f"[THEME ERR] {e}")
            return []

    def rank_news_relevance(
        self, articles: list, top_n=15, specialized_sources: list = None
    ) -> list:
        """Score and rank headlines by information density and relevance with fuzzy deduplication."""
        if not self.is_active or not articles:
            return articles[:top_n]

        specialized_sources = specialized_sources or SEMI_SOURCES

        try:
            seen_titles = []

            def is_duplicate(text):
                tokens = set(re.findall(r"\b\w{4,}\b", text.lower()))
                entities = set(re.findall(r"\b[A-Z][A-Za-z]{3,}\b", text))

                for st, se in seen_titles:
                    # 1. Jaccard Overlap
                    overlap = len(tokens & st) / (len(tokens | st) + 1)
                    if overlap > 0.35:
                        return True

                    # 2. Entity Intersection
                    common_entities = entities & se
                    if common_entities:
                        if len(tokens & st) >= 2:
                            return True
                seen_titles.append((tokens, entities))
                return False

            scored = []
            for a in articles:
                title = a.get("title", "")
                summary = a.get("summary", "")
                text = (title + " " + summary).lower()

                if is_duplicate(title):
                    continue

                length_score = min(len(text) / 200.0, 1.0)

                # V28: Specialized Source Detection (SEMI)
                is_specialized = (
                    a.get("source") in specialized_sources
                    or a.get("is_semi_trade", False)
                    or a.get("is_specialized", False)
                )

                # V28: Institutional Fluff Penalty / Specialized Bonus
                # For generic macro, penalize editorial. For SEMI, REWARD "Week in Review".
                fluff_penalty = 0
                fluff_keywords = [
                    "interview",
                    "strategy",
                    "talent",
                    "review",
                    "trends",
                    "opinion",
                    "editorial",
                    "thought leadership",
                    "week in",
                ]
                for fk in fluff_keywords:
                    if fk in text:
                        if is_specialized and fk in ["review", "week in"]:
                            fluff_penalty += 15.0  # SEMI Reviews are high-signal recaps
                        else:
                            fluff_penalty -= 10.0

                # V28: Litigation / Lawsuit Penalty
                # Hard reject legal noise (class actions, settlements, fraud)
                legal_penalty = 0
                legal_keywords = [
                    "class action",
                    "securities litigation",
                    "securities fraud",
                    "investor counsel",
                    "lawsuit",
                    "litigation",
                    "settles with",
                    "legal battle",
                    "sued for",
                    "allegedly using",
                ]
                for lk in legal_keywords:
                    if lk in text:
                        legal_penalty -= 200.0  # Nuclear Penalty

                # V28: Consumer / Social Fluff Penalty (Nuclear Filter)
                # Suppress news about shopping, social trends, kids, or lifestyle noise
                social_penalty = 0
                social_keywords = [
                    "american teens",
                    "children",
                    "kids",
                    "social media trends",
                    "lifestyle",
                    "vacation",
                    "shopping",
                    "retail",
                    "shoppers",
                    "fashion",
                    "luxury",
                    "products",
                    "memos",
                    "bags",
                    "earrings",
                    "hats",
                    "mid-priced",
                    "young shoppers",
                    "status symbol",
                ]
                for sk in social_keywords:
                    if sk in text:
                        social_penalty -= 600.0  # Extreme Nuclear Penalty

                # Hard Alpha Keywords (Investment-Grade Signal)
                alpha_words = [
                    "breakthrough",
                    "record",
                    "surge",
                    "monopoly",
                    "pivot",
                    "exclusive",
                    "bottleneck",
                    "acceleration",
                    "contract",
                    "order",
                    "guidance",
                    "forecast",
                    "undervalued",
                ]
                alpha_score = sum(3.0 for w in alpha_words if w in text)

                # V28: Sector Alpha Bonus (High Conviction Tech/Semi/Insto in Macro)
                sector_bonus = 0
                sector_keywords = [
                    "nvidia",
                    "chips",
                    "semiconductor",
                    "ai bets",
                    "gpu cluster",
                    "photonics",
                    "goldman",
                    "morgan stanley",
                    "hedge fund",
                    "tech stocks",
                    "prime brokerage",
                    "magnificent 7",
                    "mag 7",
                    "earnings",
                ]
                for sk in sector_keywords:
                    if sk in text:
                        sector_bonus += 10.0

                # VADER Sentiment Intensity
                sentiment = self.analyzer.polarity_scores(text)
                tone_score = abs(sentiment["compound"]) * 3.0

                # V28: Decoupled Scoring Integration
                # Fetch YAML-derived content score and base weight separately
                content_score = a.get("content_score", 0)
                base_weight = a.get("base_weight", a.get("score", 0))

                # Add local NLP signal
                content_score += (
                    length_score
                    + alpha_score
                    + tone_score
                    + fluff_penalty
                    + legal_penalty
                    + sector_bonus
                    + social_penalty
                )

                # V29.7.1: Macro Catalyst Bonus
                macro_keywords = [
                    "oil",
                    "fed",
                    "inflation",
                    "rates",
                    "economic",
                    "treasury",
                    "yield",
                    "prices",
                    "gdp",
                ]
                for mk in macro_keywords:
                    if mk in text:
                        content_score += 12.0

                # V29.7.1: Earnings Integrity Bonus
                if a.get("is_earn"):
                    content_score += 30.0

                # V28: Decoupled Global Relevance Floor
                # An article MUST earn its way in via financial signal, regardless of source authority.
                # Specialized sources have a lower floor (-50.0) but are STILL subject to Nuclear Hard Gates.

                # NUCLEAR HARD GATE: Direct drop if penalties exceed -100 (regardless of source)
                if (social_penalty + legal_penalty) < -100:
                    continue

                if not is_specialized:
                    if content_score < self.relevance_floor:
                        continue
                else:
                    # Specialized (ZH Tech/Markets) can have lower scores but still need some signal
                    if content_score < -50.0:
                        continue

                # Re-couple for final ranking
                final_score = base_weight + content_score
                a["final_score"] = final_score
                scored.append((a, final_score))

            # Sort by score descending
            ranked = [s[0] for s in sorted(scored, key=lambda x: x[1], reverse=True)]
            return ranked[:top_n]
        except Exception as e:
            print(f"[NLP ERR] Ranking failed: {e}")
            return articles[:top_n]
