# V28.8.1: Sovereign Market Synopsis Scraper (Hardened)
import logging
import re
from pathlib import Path

from curl_cffi import requests as cffi_requests

log = logging.getLogger(__name__)


class MarketSynopsisScraper:
    """
    Sovereign Hybrid Scraper: Transitions between institutional sources
    based on the active market session with multi-source fallback.
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
        if len(text) > 1000:
            text = text[:997] + "..."
        return text

    def _is_junk(self, text):
        if not text or len(text) < 80:
            return True
        low = text.lower()

        # V28.8.2: Hardened Placeholder Rejection
        if "data is a real-time snapshot" in low or "delayed at least 15 minutes" in low:
            return True
        if "global business and financial news" in low and "stock quotes" in low:
            return True
        if "licensing & reprints" in low or "site map" in low or "careers" in low:
            return True
        if "check back here for the latest" in low:
            return True

        sample = text[:300]
        # Require a higher editorial signal density for short paragraphs
        editorial_matches = len(self._EDITORIAL_KEYWORDS.findall(text))
        if editorial_matches < 2:
            return True

        if len(self._JUNK_PATTERNS.findall(sample)) >= 2:
            return True
        return False

    def _extract_stockmarketwatch(self, html):
        # 1. Primary: data-article-body signature
        body_match = re.search(r'data-article-body="([^"]+)"', html)
        if body_match:
            cleaned = self._clean_text(body_match.group(1))
            if len(cleaned) > 100 and not self._is_junk(cleaned):
                return cleaned
        # 2. Secondary: DOM search
        p_matches = re.findall(r"<p\b[^>]*>(.*?)</p>", html, re.DOTALL | re.IGNORECASE)
        for p in p_matches:
            cleaned = self._clean_text(p)
            if len(cleaned) > 150 and not self._is_junk(cleaned):
                return cleaned
        return ""

    def _extract_cnbc(self, html, depth=0):
        if depth > 1:
            return ""  # Prevent loops

        # V28.8.2: Multi-Signature Detection (FeaturedContent vs LiveBlogBody)
        signatures = [
            "FeaturedContent-articleBody",
            "LiveBlogBody-articleBody",
            "ArticleBody-articleBody",
            "LiveBlog-body",
            "LiveBlog-post",
        ]

        found_signature = False
        start_idx = -1

        for sig in signatures:
            idx = html.find(sig)
            if idx != -1:
                log.info(f"[SYNOPSIS] CNBC Signature Match: {sig}")
                start_idx = idx
                found_signature = True
                break

        if found_signature:
            # Slicing is safer than a complex regex for the end boundary
            end_idx = html.find("ArticleFooter-articleFooter", start_idx)
            if end_idx == -1:
                end_idx = html.find("</footer>", start_idx)
            if end_idx == -1:
                end_idx = html.find("SidebarArticle-sidebar", start_idx)

            target_html = html[start_idx:end_idx] if end_idx != -1 else html[start_idx:]

            p_matches = re.findall(r"<p\b[^>]*>(.*?)</p>", target_html, re.DOTALL | re.IGNORECASE)
            sub_p = [self._clean_text(p) for p in p_matches]
            sub_p = [p for p in sub_p if not self._is_junk(p)]

            # Capture first 2 paragraphs for a richer recap if available
            if len(sub_p) >= 2:
                return f"{sub_p[0]} {sub_p[1]}"
            return sub_p[0] if sub_p else ""

        # 2. If not, assume landing page and find the latest "live-updates" link
        match = re.search(r'href="([^"]+stock-market-today-live-updates[^"]*)"', html)
        if match:
            url = match.group(1)
            if not url.startswith("http"):
                url = "https://www.cnbc.com" + url
            log.info(f"[SYNOPSIS] CNBC landing page detected. Jumping to: {url}")
            try:
                r = cffi_requests.get(
                    url, headers=self.headers, impersonate="chrome146", timeout=10
                )
                if r.status_code == 200:
                    return self._extract_cnbc(r.text, depth + 1)
            except Exception as e:
                log.error(f"[SYNOPSIS] CNBC jump error: {e}")

        return ""

    def _extract_edj(self, html):
        p_matches = re.findall(r"<p\b[^>]*>(.*?)</p>", html, re.DOTALL | re.IGNORECASE)
        for p in p_matches:
            cleaned = self._clean_text(p)
            if len(cleaned) > 150 and not self._is_junk(cleaned):
                return cleaned
        return ""

    def fetch_synopsis(self, session_label):
        """
        Hardened Dispatcher: Tries target source, then falls back to healthy alternatives.
        """
        lbl = "PRE" if session_label in ["PM", "PRE"] else session_label
        if lbl in ["AH", "POST", "OVN", "CLOSED"]:
            lbl = "POST"
        elif lbl in ["LIVE", "REG"]:
            lbl = "MID"

        # Rotation order: Target -> PRE -> MID -> POST
        to_try = list(dict.fromkeys([lbl, "PRE", "MID", "POST"]))

        for key in to_try:
            if key not in self.SOURCES:
                continue
            src = self.SOURCES[key]
            log.info(f"[SYNOPSIS] Attempting {src['name']} (Session: {session_label})")

            try:
                r = cffi_requests.get(
                    src["url"], headers=self.headers, impersonate="chrome146", timeout=12
                )
                if r.status_code != 200:
                    continue

                text = ""
                if src["type"] == "STOCKMARKETWATCH":
                    text = self._extract_stockmarketwatch(r.text)
                elif src["type"] == "CNBC":
                    text = self._extract_cnbc(r.text)
                elif src["type"] == "EDJ":
                    text = self._extract_edj(r.text)

                if text:
                    log.info(f"[SYNOPSIS] SUCCESS \u2192 {src['name']}")
                    return {"text": text, "source": src["name"]}
            except Exception as e:
                log.error(f"[SYNOPSIS] Source {src['name']} error: {e}")

        log.error("[SYNOPSIS] All sources exhausted.")
        return None
