import random
import re


class PaywallIntelligence:
    """
    V29.0: Institutional Paywall Intelligence Engine.
    Ports bypass logic from the FreePaywall (Bypass Paywalls Clean) database
    to enable high-fidelity scraping for the AI engine.
    """

    # Standard Institutional User-Agents
    GOOGLE_BOT = "Mozilla/5.0 (compatible; Google-InspectionTool/1.0)"
    CHROME_146 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.7000.100 Safari/537.36"
    FACEBOOK_BOT = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"

    RULES = {
        "bloomberg.com": {
            "block_regex": r"\.bwbx\.io\/s3\/fence\/",
            "useragent": GOOGLE_BOT,
            "referer": "https://www.google.com/",
        },
        "wsj.com": {
            "referer": "https://www.drudgereport.com/",
            "useragent": CHROME_146,
            "remove_cookies": ["wsj_session", "djcs_session"],
        },
        "barrons.com": {
            "block_regex": r"\.cxense\.com\/",
            "referer": "https://www.drudgereport.com/",
            "useragent": CHROME_146,
        },
        "nytimes.com": {
            "useragent": GOOGLE_BOT,
            "block_regex": r"(\.nytimes\.com\/(meter\.js|svc\/onsite-messaging\/query)|mwcm\.nyt\.com\/.+\.js)",
        },
        "economist.com": {
            "block_regex": r"(\/zephr\/feature|\.economist\.com\/(latest\/wall-ui|script)\.js)",
            "useragent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36 Liskov",
        },
        "ft.com": {"useragent": GOOGLE_BOT, "referer": "https://www.google.com/"},
        "seekingalpha.com": {"useragent": GOOGLE_BOT, "referer": "https://www.google.com/"},
    }

    @classmethod
    def get_rules(cls, url):
        """Returns bypass rules for a given URL's domain."""
        domain = cls.get_domain(url)
        return cls.RULES.get(domain, {})

    @staticmethod
    def get_domain(url):
        """Extracts the base domain (e.g. bloomberg.com) from a URL."""
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if match:
            domain = match.group(1).lower()
            # Handle subdomains by looking for known suffixes
            for known in [
                "bloomberg.com",
                "wsj.com",
                "barrons.com",
                "nytimes.com",
                "economist.com",
                "ft.com",
                "seekingalpha.com",
            ]:
                if known in domain:
                    return known
        return ""

    @classmethod
    def apply_stealth_headers(cls, url, headers):
        """Injects bypass headers into a request header dict."""
        rules = cls.get_rules(url)
        if not rules:
            return headers

        if "useragent" in rules:
            headers["User-Agent"] = rules["useragent"]
        if "referer" in rules:
            headers["Referer"] = rules["referer"]

        # Add random jitter to Chrome headers if not spoofing a bot
        if headers.get("User-Agent") == cls.CHROME_146:
            headers["User-Agent"] = headers["User-Agent"].replace(
                ".100", f".{random.randint(100, 250)}"
            )

        return headers

    @classmethod
    def get_playwright_block_patterns(cls, url):
        """Returns a list of regex patterns for Playwright to block."""
        rules = cls.get_rules(url)
        patterns = []
        if "block_regex" in rules:
            patterns.append(rules["block_regex"])

        # Global Paywall Scripts
        global_blocks = [
            r"\.tinypass\.com\/",
            r"\.piano\.io\/",
            r"\.cxense\.com\/",
            r"\.sophi\.io\/",
            r"\.zephr\.com\/",
            r"\.poool\.fr\/",
        ]
        patterns.extend(global_blocks)
        return patterns


class DeepScraper:
    """
    V29.0: Institutional Content Extractor.
    Uses PaywallIntelligence to fetch and extract full article bodies.
    """

    @staticmethod
    async def extract_bloomberg(html: str) -> str:
        # Bloomberg often keeps the text in a JSON blob or hidden div
        # We try to grab the main article body
        match = re.search(
            r'<div[^>]*class="[^"]*body-copy[^"]*"[^>]*>(.*?)</div>\s*<div', html, re.DOTALL
        )
        if not match:
            match = re.search(r"<article[^>]*>(.*?)</article>", html, re.DOTALL)
        if match:
            content = re.sub(r"<[^>]+>", "", match.group(1))
            return content.strip()
        return ""

    @staticmethod
    async def extract_wsj(html: str) -> str:
        # WSJ uses article-content blocks
        match = re.search(
            r'<div[^>]*class="[^"]*article-content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL
        )
        if match:
            content = re.sub(r"<[^>]+>", "", match.group(1))
            return content.strip()
        return ""

    @staticmethod
    async def extract_generic(html: str) -> str:
        # Fallback for other sites: find the longest text block
        # Simple heuristic: remove scripts/styles and grab main text
        clean = re.sub(
            r"<(script|style|nav|header|footer)[^>]*>.*?</\1>",
            "",
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        clean = re.sub(r"<[^>]+>", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        # Return first 2000 chars if it's substantial
        return clean[:3000]

    @classmethod
    async def fetch_full_content(cls, url: str) -> str:
        from curl_cffi.requests import AsyncSession

        domain = PaywallIntelligence.get_domain(url)
        if not domain:
            return ""

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        headers = PaywallIntelligence.apply_stealth_headers(url, headers)

        try:
            async with AsyncSession() as session:
                resp = await session.get(url, headers=headers, timeout=15, impersonate="chrome110")
                if resp.status_code != 200:
                    return ""

                html = resp.text
                if domain == "bloomberg.com":
                    return await cls.extract_bloomberg(html)
                elif domain == "wsj.com":
                    return await cls.extract_wsj(html)
                else:
                    return await cls.extract_generic(html)
        except Exception as e:
            print(f"[DeepScraper ERR] {url}: {e}")
            return ""
