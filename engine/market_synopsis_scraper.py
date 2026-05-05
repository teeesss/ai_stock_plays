# V28.8.9: Sovereign Market Synopsis Scraper (Hybrid Cache + Resilience)
import asyncio
import json
import logging
import os
import re
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

import feedparser
from curl_cffi import requests as cffi_requests

log = logging.getLogger(__name__)


class MarketSynopsisScraper:
    """
    Sovereign Hybrid Scraper: Transitions between institutional sources
    based on the active market session with multi-source fallback.
    V28.8.9: Implements a hybrid cache model for AI intelligence to bypass
    environment-specific browser constraints.
    """

    SOURCES = {
        "PRE": {
            "url": "https://stockmarketwatch.com/live/stock-market-today",
            "name": "STOCKMARKETWATCH",
            "type": "STOCKMARKETWATCH",
        },
        "MID": {
            "url": "https://www.cnbc.com/stock-market-daily-recap/",
            "name": "CNBC LIVE",
            "type": "CNBC",
        },
        "POST": {
            "url": "https://www.edwardjones.com/us-en/market-news-insights/stock-market-news/daily-market-recap",
            "name": "EDWARD JONES",
            "type": "EDJ",
        },
    }

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.cache_path = Path("database/ai_intel_cache.json")

    # Junk patterns for rejection
    _JUNK_PATTERNS = re.compile(
        r"(upgrade to premium|u\.s\. markets open in|markets open in|start your day with|yahoo finance|advertisement|sign in|get the app|your portfolio|watchlist|screeners|currencies|rates|commodities|cryptocurrencies|europe markets|asia markets|russell 2000 futures|nasdaq futures|dow futures|s&p futures|vix|crude oil|bitcoin usd|gold|live updates|live market updates|major indices|us exchanges|technical breadth|economic calendar|short squeeze|top stocks|ai & machine learning|semiconductors|cybersecurity|cloud & saas|biotech|oncology|clean energy|oil & gas|banking & lending|fintech|metal prices|gold price|silver price|copper price|platinum price|palladium price|try again|track all markets|tradingview|data is a real-time snapshot|delayed at least 15 minutes|global business and financial news|stock quotes, and market data|and analysis|licensing & reprints|site map|careers|contact|help|all rights reserved|market data terms of use)",
        re.IGNORECASE,
    )

    # Editorial keywords for confirmation
    _EDITORIAL_KEYWORDS = re.compile(
        r"(market|stock|investor|trade|equit|index|indices|fed|rate|economy|earning|gdp|inflation|bond|treasury|sector|rally|sell.off|decline|surge|gain|loss|quarter|forecast|analyst|percent|basis point|s&p|nasdaq|dow|oil|crude|energy|yield)",
        re.IGNORECASE,
    )

    def _clean_text(self, text):
        if not text:
            return ""
        text = re.sub(r"<[^>]+>", "", text)
        text = (
            text.replace("&nbsp;", " ")
            .replace("&quot;", '"')
            .replace("&apos;", "'")
            .replace("&amp;", "&")
        )
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 1500:
            text = text[:1497] + "..."
        return text

    def _is_junk(self, text):
        if not text or len(text) < 80:
            return True
        low = text.lower()
        if "data is a real-time snapshot" in low or "delayed at least 15 minutes" in low:
            return True
        if "global business and financial news" in low and "stock quotes" in low:
            return True
        if "licensing & reprints" in low or "site map" in low or "careers" in low:
            return True
        if "check back here for the latest" in low:
            return True

        editorial_matches = len(self._EDITORIAL_KEYWORDS.findall(text))
        if editorial_matches < 2:
            return True

        sample = text[:300]
        if len(self._JUNK_PATTERNS.findall(sample)) >= 2:
            return True
        return False

        return ""

    def _extract_edward_jones(self, html):
        """
        V30.0: Hardened Edward Jones scraper.
        Extracts high-alpha recap bullets while strictly stripping IPC boilerplate and author lines.
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Edward Jones recaps are typically in <li> or <p> tags starting with "- "
        potential_points = []

        # First try finding the main content div to avoid footer noise
        main_content = soup.find("div", class_="market-news-insights") or soup

        items = main_content.find_all(["p", "li"])
        for item in items:
            text = item.get_text().strip()
            # Clean up non-breaking spaces and other encoding artifacts
            text = text.replace("\xa0", " ")

            # Identify recap bullets (usually start with "-" or a dash)
            if text.startswith(("-", "–", "—")) or " – " in text or " - " in text:
                # Normalize dash encoding artifacts
                text = text.replace("\u2013", "-").replace("\u2014", "-")

                # Stop if we hit the author/IPC section
                if any(
                    x in text
                    for x in [
                        "Investment Policy Committee",
                        "James McCann",
                        "Brock Weimer",
                        "Mona Mahajan",
                        "Brian Therien",
                        "Angelo Kourkafas",
                    ]
                ):
                    break

                if len(text) > 100 and not self._is_junk(text):
                    # V30.2: Defensive narrative suppression
                    if not any(
                        bad in text.upper() for bad in ["SESSION PERFORMANCE", "DISCLOSURE", "IPC"]
                    ):
                        potential_points.append(text)

        if potential_points:
            # Join top 3 points, ensuring no IPC disclosures leak
            recap = " ".join(potential_points[:3])
            # Nuclear strip of any trailing IPC noise or boilerplate
            recap = re.split(r"Investment Policy Committee", recap, flags=re.I)[0].strip()
            recap = recap.replace("SESSION PERFORMANCE", "Market Dynamics")
            return recap
        return ""

    async def _extract_cnbc_async(self, html, depth=0):
        if depth > 1:
            return ""
        signatures = [
            "FeaturedContent-articleBody",
            "LiveBlogBody-articleBody",
            "ArticleBody-articleBody",
        ]
        start_idx = -1
        for sig in signatures:
            idx = html.find(sig)
            if idx != -1:
                start_idx = idx
                break

        if start_idx != -1:
            end_idx = html.find("ArticleFooter-articleFooter", start_idx)
            if end_idx == -1:
                end_idx = html.find("</footer>", start_idx)
            target_html = html[start_idx:end_idx] if end_idx != -1 else html[start_idx:]
            p_matches = re.findall(r"<p\b[^>]*>(.*?)</p>", target_html, re.DOTALL | re.IGNORECASE)
            sub_p = [
                self._clean_text(p) for p in p_matches if not self._is_junk(self._clean_text(p))
            ]
            if len(sub_p) >= 2:
                return f"{sub_p[0]} {sub_p[1]}"
            return sub_p[0] if sub_p else ""

        match = re.search(r'href="([^"]+stock-market-today-live-updates[^"]*)"', html)
        if match:
            url = match.group(1)
            if not url.startswith("http"):
                url = "https://www.cnbc.com" + url
            try:
                loop = asyncio.get_event_loop()
                r = await loop.run_in_executor(
                    None,
                    lambda: cffi_requests.get(
                        url, headers=self.headers, impersonate="chrome146", timeout=10
                    ),
                )
                if r.status_code == 200:
                    return await self._extract_cnbc_async(r.text, depth + 1)
            except:
                pass
        return ""

    async def _fetch_rss_intelligence(self, query_type="PRE"):
        """
        V29.0: High-fidelity synthesis via Google News RSS + Local NLP.
        Bypasses brittle web scraping by aggregating 100+ headlines.
        """
        queries = {
            "PRE": "stock market today premarket movers when:1d",
            "MID": "stock market live updates today when:1d",
            "POST": "stock market closing recap today when:1d",
        }
        query = queries.get(query_type, queries["MID"])
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

        log.info(f"[SYNOPSIS] Aggregating RSS Intelligence: {query}")
        try:
            feed = await asyncio.get_event_loop().run_in_executor(
                None, lambda: feedparser.parse(rss_url)
            )
            if not feed.entries:
                return None

            # Convert RSS entries to normalized article objects for NLP ranking
            articles = []
            for entry in feed.entries:
                # V30.2: Aggressively strip HTML from summaries to prevent URL-split corruption
                raw_summary = entry.get("summary", "")
                clean_summary = re.sub(r"<[^>]+>", "", raw_summary)

                articles.append(
                    {
                        "title": entry.title,
                        "summary": clean_summary,
                        "link": entry.link,
                        "source": entry.get("source", {}).get("title", "Google News"),
                        "content_score": 0,
                        "base_weight": 10,
                        "is_specialized": True,  # V29: Bypass high macro floor for snippets
                    }
                )

            # Initialize Local NLP (VADER + FinVADER)
            try:
                from local_nlp import LocalIntelligenceSynthesizer
            except ImportError:
                from engine.local_nlp import LocalIntelligenceSynthesizer

            nlp = LocalIntelligenceSynthesizer()

            # Rank and prune noise via FinVADER / Keyword density
            ranked = nlp.rank_news_relevance(articles, top_n=15)
            if not ranked:
                log.warning("[SYNOPSIS] No articles passed the relevance floor.")
                return None

            # Synthesize dense narrative
            # We use "Neutral" as vibe fallback; the orchestrator will flair it later
            intel_data, used_links = nlp.synthesize_market_narrative(ranked, vibe="Neutral")

            # V30.2: Defensive filtering before return
            clean_points = []
            for p in intel_data.get("points", []):
                if any(bad in p.upper() for bad in ["SESSION PERFORMANCE", "DISCLOSURE", "IPC"]):
                    continue
                clean_points.append(p)

            if not clean_points:
                return None

            return {
                "points": clean_points,
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "source": "SOVEREIGN INTEL V30.2",
                "focal_point": intel_data.get("focal_point", "Market Pulse"),
            }
        except Exception as e:
            log.error(f"[SYNOPSIS] RSS Synthesis Error: {e}")
            return None

    async def _fetch_ai_intel(self):
        """DEPRECATED (V29.0): Brittle Playwright scraping preserved as emergency fallback only."""
        # 1. Check Intelligence Cache (Sovereign Out-of-Band Loop)
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r") as f:
                    data = json.load(f)
                    ts_str = data.get("timestamp", datetime.now().isoformat())
                    ts = datetime.fromisoformat(ts_str).replace(tzinfo=None)
                    now = datetime.now().replace(tzinfo=None)

                    if now - ts < timedelta(minutes=60):
                        log.info(
                            f"[SYNOPSIS] AI Intel loaded from Sovereign Cache (@ {ts.strftime('%I:%M %p')})"
                        )
                        text = data["text"]
                        # V30.2: Mandatory filter for legacy cache leaks
                        if "SESSION PERFORMANCE" in text:
                            text = text.replace("SESSION PERFORMANCE", "Market Dynamics")

                        return {
                            "text": text,
                            "timestamp": ts.strftime("%I:%M %p"),
                            "source": "SOVEREIGN AI",
                        }
            except Exception as e:
                log.warning(f"[SYNOPSIS] Cache read error: {e}")

        return {"text": None, "timestamp": None}

    async def fetch_synopsis(self, session_label):
        """
        Hardened V30.0: Hybrid RSS + Institutional Scraper Pipeline.
        Prioritizes high-fidelity synthesis with specialized fallback for Edward Jones.
        """
        lbl = "PRE" if session_label in ["PM", "PRE"] else session_label
        if lbl in ["AH", "POST", "OVN", "CLOSED"]:
            lbl = "POST"
        elif lbl in ["LIVE", "REG"]:
            lbl = "MID"

        # V30.0: Priority 1 - High-alpha Institutional Scrape (EDJ) for Post-Market
        if lbl == "POST":
            src = self.SOURCES["POST"]
            try:
                loop = asyncio.get_event_loop()
                r = await loop.run_in_executor(
                    None,
                    lambda: cffi_requests.get(
                        src["url"], headers=self.headers, impersonate="chrome146", timeout=10
                    ),
                )
                if r.status_code == 200:
                    edj_text = self._extract_edward_jones(r.text)
                    if edj_text:
                        # Feed the high-quality scrape into the Narrative Engine V2
                        try:
                            from local_nlp import LocalIntelligenceSynthesizer
                        except ImportError:
                            from engine.local_nlp import LocalIntelligenceSynthesizer

                        nlp = LocalIntelligenceSynthesizer()
                        # Use the EJ text as the lead paragraph for the narrative
                        intel_data, _ = nlp.synthesize_market_narrative(
                            [], vibe="Neutral", scraped_lead=edj_text
                        )
                        points = intel_data.get("points", [])

                        if points:
                            return [
                                {
                                    "points": points,
                                    "timestamp": datetime.now().strftime("%I:%M %p"),
                                    "source": "EDWARD JONES V30.2",
                                    "focal_point": "Market Recap",
                                }
                            ]
            except Exception as e:
                log.warning(f"[SYNOPSIS] EDJ Scrape failed: {e}")

        # V30.0: Priority 2 - RSS-driven Intelligence Synthesis
        res = await self._fetch_rss_intelligence(lbl)
        if res and res.get("text"):
            return [res]

        # Emergency Fallback: Last known good AI Intel from cache
        legacy = await self._fetch_ai_intel()
        if legacy and legacy.get("text"):
            return [legacy]

        return []
