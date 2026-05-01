# V28.8.9: Sovereign Market Synopsis Scraper (Hybrid Cache + Resilience)
import asyncio
import json
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

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

    def _extract_stockmarketwatch(self, html):
        body_match = re.search(r'data-article-body="([^"]+)"', html)
        if body_match:
            cleaned = self._clean_text(body_match.group(1))
            if len(cleaned) > 100 and not self._is_junk(cleaned):
                return cleaned
        p_matches = re.findall(r"<p\b[^>]*>(.*?)</p>", html, re.DOTALL | re.IGNORECASE)
        for p in p_matches:
            cleaned = self._clean_text(p)
            if len(cleaned) > 150 and not self._is_junk(cleaned):
                return cleaned
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

    async def _fetch_ai_intel(self):
        """Prioritizes the local intelligence cache, then attempts a resilient live fetch."""
        # 1. Check Intelligence Cache (Sovereign Out-of-Band Loop)
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r") as f:
                    data = json.load(f)
                    ts_str = data.get("timestamp", datetime.now().isoformat())
                    # Normalize to naive for comparison
                    ts = datetime.fromisoformat(ts_str).replace(tzinfo=None)
                    now = datetime.now().replace(tzinfo=None)

                    # Cache valid for 60 minutes
                    if now - ts < timedelta(minutes=60):
                        log.info(
                            f"[SYNOPSIS] AI Intel loaded from Sovereign Cache (@ {ts.strftime('%I:%M %p')})"
                        )
                        return {
                            "text": data["text"],
                            "timestamp": ts.strftime("%I:%M %p"),
                            "source": "SOVEREIGN AI",
                        }
            except Exception as e:
                log.warning(f"[SYNOPSIS] Cache read error: {e}")

        # 2. Resilient Live Fetch (Last Resort in restricted environments)
        log.info("[STEALTH] Initializing Sovereign AI Live Fetch (Final Resort)...")
        try:
            try:
                from stealth_navigator import StealthNavigator
            except ImportError:
                from engine.stealth_navigator import StealthNavigator
        except:
            return {"text": None, "timestamp": None}

        nav = StealthNavigator(headless=True)
        try:
            await nav.initialize()
            page = await nav.context.new_page()
            # Try Perplexity Direct (Encoded)
            query = "stock market today news overview".replace(" ", "+")
            await page.goto(
                f"https://www.perplexity.ai/search?q={query}",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            await asyncio.sleep(12)

            el = await page.locator("div.prose").first
            if await el.is_visible():
                txt = await el.inner_text()
                if txt and len(txt) > 200:
                    return {
                        "text": txt.strip(),
                        "timestamp": datetime.now().strftime("%I:%M %p"),
                        "source": "SOVEREIGN AI",
                    }
            return {"text": None, "timestamp": None}
        except:
            return {"text": None, "timestamp": None}
        finally:
            try:
                await nav.close()
            except:
                pass

    async def fetch_synopsis(self, session_label):
        """Hardened Async Dispatcher: Aggregates multiple fresh sources (AI, Fallbacks)."""
        lbl = "PRE" if session_label in ["PM", "PRE"] else session_label
        if lbl in ["AH", "POST", "OVN", "CLOSED"]:
            lbl = "POST"
        elif lbl in ["LIVE", "REG"]:
            lbl = "MID"

        results = []

        # Build prioritized stack based on session
        to_try = ["AI", lbl]
        if lbl == "POST":
            # After hours: Add fallbacks for completeness
            to_try.extend(["MID", "PRE"])
        elif lbl == "MID":
            # Live market: Focus on MID/AI only. Skip POST (EDJ) until AH.
            to_try.extend(["PRE"])
        else:
            # PRE session
            to_try.extend(["MID"])

        seen_keys = set()

        for key in to_try:
            if key in seen_keys:
                continue
            seen_keys.add(key)

            if key == "AI":
                res = await self._fetch_ai_intel()
                if res and res.get("text"):
                    source_tag = res.get("source", "SOVEREIGN AI")
                    results.append(
                        {
                            "text": res["text"],
                            "source": source_tag,
                            "timestamp": res.get("timestamp"),
                        }
                    )
                continue

            if key not in self.SOURCES:
                continue
            src = self.SOURCES[key]
            log.info(f"[SYNOPSIS] Gathering Fallback: {src['name']}")
            try:
                loop = asyncio.get_event_loop()
                r = await loop.run_in_executor(
                    None,
                    lambda: cffi_requests.get(
                        src["url"], headers=self.headers, impersonate="chrome146", timeout=10
                    ),
                )
                if r.status_code != 200:
                    continue
                text = ""
                if src["type"] == "STOCKMARKETWATCH":
                    text = self._extract_stockmarketwatch(r.text)
                elif src["type"] == "CNBC":
                    text = await self._extract_cnbc_async(r.text)
                elif src["type"] == "EDJ":
                    text = self._extract_stockmarketwatch(r.text)

                if text:
                    # Use current time as fallback timestamp for institutional if not found in text
                    results.append(
                        {
                            "text": text,
                            "source": src["name"],
                            "timestamp": datetime.now().strftime("%I:%M %p"),
                        }
                    )
            except Exception as e:
                log.error(f"[SYNOPSIS] Source {src['name']} error: {e}")

        # Return list of results (prioritize AI first as it's already first in to_try)
        return results if results else None
