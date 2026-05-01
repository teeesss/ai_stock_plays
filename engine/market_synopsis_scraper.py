# V28.8: Sovereign Market Synopsis Scraper
import logging
import re
from pathlib import Path

from curl_cffi import requests as cffi_requests

# V28: Hierarchy Leader Error Monitoring
try:
    from engine import error_monitor
except ImportError:
    import error_monitor

log = logging.getLogger(__name__)


class MarketSynopsisScraper:
    """
    Sovereign Hybrid Scraper: Transitions between institutional sources
    based on the active market session.
    """

    SOURCES = {
        "PRE": {
            "url": "https://finance.yahoo.com/topic/morning-brief/",
            "name": "YAHOO FINANCE",
            "type": "YAHOO",
        },
        "MID": {"url": "https://www.cnbc.com/world-markets/", "name": "CNBC LIVE", "type": "CNBC"},
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

    # Patterns that signal Yahoo nav/promo/ad junk — never editorial content
    _JUNK_PATTERNS = re.compile(
        r"(upgrade to premium|u\.s\. markets open in|markets open in|morning brief|start your day with|yahoo finance|advertisement|sign in|get the app|your portfolio|watchlist|screeners|currencies|rates|commodities|cryptocurrencies|europe markets|asia markets|russell 2000 futures|nasdaq futures|dow futures|s&p futures|vix|crude oil|bitcoin usd|gold)",
        re.IGNORECASE,
    )

    # Keywords that confirm a paragraph is genuine financial editorial
    _EDITORIAL_KEYWORDS = re.compile(
        r"(market|stock|investor|trade|equit|index|indices|fed|rate|economy|earning|gdp|inflation|bond|treasury|sector|rally|sell.off|decline|surge|gain|loss|quarter|forecast|analyst|percent|basis point)",
        re.IGNORECASE,
    )

    def _clean_text(self, text):
        if not text:
            return ""
        # Strip HTML tags and entities
        text = re.sub(r"<[^>]+>", "", text)
        text = (
            text.replace("&nbsp;", " ")
            .replace("&quot;", '"')
            .replace("&apos;", "'")
            .replace("&amp;", "&")
        )
        text = re.sub(r"\s+", " ", text).strip()
        # Cap at 600 chars for a meaningful paragraph
        if len(text) > 600:
            text = text[:597] + "..."
        return text

    def _is_junk(self, text):
        """Return True if text is nav/promo/ad content, not editorial."""
        if not text or len(text) < 80:
            return True
        # High junk-to-length ratio: more than 3 junk pattern hits in first 300 chars
        sample = text[:300]
        junk_hits = len(self._JUNK_PATTERNS.findall(sample))
        if junk_hits >= 3:
            return True
        # Must contain at least one editorial keyword
        if not self._EDITORIAL_KEYWORDS.search(text):
            return True
        return False

    def fetch_synopsis(self, session_label):
        """
        Main entry point. Map session to source and extract.
        """
        lbl = "PRE" if session_label in ["PM", "PRE"] else session_label
        if lbl in ["AH", "POST", "OVN", "CLOSED"]:
            lbl = "POST"

        if lbl not in self.SOURCES:
            lbl = "POST"

        source = self.SOURCES[lbl]
        log.info(f"[SYNOPSIS] Targeting {source['name']} for session {session_label}")

        try:
            r = cffi_requests.get(
                source["url"], headers=self.headers, impersonate="chrome146", timeout=15
            )
            if r.status_code != 200:
                log.warning(f"[SYNOPSIS] {source['name']} returned status {r.status_code}")
                return None

            html = r.text
            synopsis = ""
            headline = ""

            if source["type"] == "YAHOO":
                # 1. Prioritize morning-brief article links, then general news links
                links = re.findall(r'href="([^"]+morning-brief[^"]+)"', html)
                if not links:
                    links = re.findall(r'href="([^"]+/news/[^"]+)"', html)

                if links:
                    article_url = links[0]
                    if article_url.startswith("/"):
                        article_url = "https://finance.yahoo.com" + article_url

                    ra = cffi_requests.get(
                        article_url, headers=self.headers, impersonate="chrome146", timeout=10
                    )
                    if ra.status_code == 200:
                        h_match = re.search(r"<h1[^>]*>(.*?)</h1>", ra.text)
                        headline = h_match.group(1) if h_match else ""
                        # Extract paragraphs — prefer caas-body paragraphs (article body)
                        p_matches = re.findall(
                            r'<p[^>]*class="[^"]*caas[^"]*"[^>]*>(.*?)</p>', ra.text, re.DOTALL
                        )
                        if not p_matches:
                            # Fallback: any <p> tag, but filter strictly for editorial content
                            p_matches = re.findall(r"<p[^>]*>(.*?)</p>", ra.text, re.DOTALL)
                        # Clean each candidate and reject junk
                        good_p = []
                        for p in p_matches:
                            cleaned = self._clean_text(p)
                            if len(cleaned) > 100 and not self._is_junk(cleaned):
                                good_p.append(cleaned)
                            if len(good_p) >= 2:
                                break
                        synopsis = " ".join(good_p)

            elif source["type"] == "CNBC":
                # Find any link containing "stock-market-today"
                links = re.findall(
                    r'href="(https://www.cnbc.com/\d{4}/\d{2}/\d{2}/stock-market-today-live-updates.html)"',
                    html,
                )
                if not links:
                    links = re.findall(
                        r'href="(/20\d{2}/\d{2}/\d{2}/stock-market-today-live-updates.html)"', html
                    )

                article_url = links[0] if links else source["url"]
                if article_url.startswith("/"):
                    article_url = "https://www.cnbc.com" + article_url

                ra = cffi_requests.get(
                    article_url, headers=self.headers, impersonate="chrome146", timeout=10
                )
                if ra.status_code == 200:
                    h_match = re.search(r"<h1[^>]*>(.*?)</h1>", ra.text)
                    headline = h_match.group(1) if h_match else ""
                    # Intro snippet or first paragraphs
                    snippet = re.search(
                        r'<div class="LiveBlogHeader-snippet"[^>]*>(.*?)</div>', ra.text, re.DOTALL
                    )
                    if snippet:
                        synopsis = snippet.group(1)
                    else:
                        p_matches = re.findall(r"<p>(.*?)</p>", ra.text)
                        sub_p = [p for p in p_matches if len(p) > 80]
                        synopsis = sub_p[0] if sub_p else ""

            else:  # EDJ
                h_match = re.search(r"<h1[^>]*>(.*?)</h1>", html)
                headline = h_match.group(1) if h_match else ""
                p_matches = re.findall(r"<p[^>]*>(.*?)</p>", html)
                # Find the most substantive paragraph
                for p in p_matches:
                    if len(p) > 150 and ("market" in p.lower() or "investor" in p.lower()):
                        synopsis = p
                        break

            cleaned_headline = self._clean_text(headline)
            # For non-Yahoo sources, clean the synopsis here (Yahoo already cleaned per-paragraph)
            if source["type"] != "YAHOO":
                cleaned_body = self._clean_text(synopsis)
            else:
                cleaned_body = synopsis  # Already cleaned inline above

            # Final quality gate: reject if body is empty or still looks like junk
            if cleaned_body and not self._is_junk(cleaned_body):
                log.info(f"[SYNOPSIS] OK — {source['name']} | {len(cleaned_body)} chars")
                return {
                    "headline": cleaned_headline,
                    "text": cleaned_body,
                    "source": source["name"],
                    "session": session_label,
                }
            else:
                log.warning(
                    f"[SYNOPSIS] Rejected low-quality body from {source['name']} — likely nav/promo junk"
                )

        except Exception as e:
            log.error(f"[SYNOPSIS] Failed to extract from {source['name']}: {e}")
            error_monitor.log_error("SYNOPSIS_EXTRACT_FAIL", str(e))

        return None


if __name__ == "__main__":
    # Test harness
    logging.basicConfig(level=logging.INFO)
    scraper = MarketSynopsisScraper()
    for lbl in ["PRE", "MID", "POST"]:
        res = scraper.fetch_synopsis(lbl)
        print(f"--- {lbl} ---")
        print(res)
