import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../engine')))
import asyncio
import random
import json
import time
from playwright.async_api import async_playwright
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# SPEC 2026: Identity Sync
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.7727.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.6478.182 Safari/537.36"
]

class YahooNewsFetcher:
    """Ultimate Stealth News Fetcher (Playwright Core). Human Persona Active."""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.current_ua = random.choice(USER_AGENTS)

    def get_vibe(self, text):
        """Calculates VADER sentiment score."""
        return self.analyzer.polarity_scores(text)['compound']

    async def fetch_batch(self, tickers, days=7):
        """Fetches news with 2026-grade stealth. Filtering by age."""
        master_news = {}
        cutoff_ts = int(time.time()) - (days * 86400)
        
        async with async_playwright() as p:
            # 1. Launch with Fingerprint Masking
            browser = await p.chromium.launch(headless=True, args=[
                "--disable-blink-features=AutomationControlled",
                f"--user-agent={self.current_ua}"
            ])
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self.current_ua
            )
            
            # Mask Hardware Level
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            for symbol in tickers:
                try:
                    clean_symbol = symbol.strip().replace("$", "").split(" / ")[0]
                    print(f"[STEALTH] Yahoo News Sync: {clean_symbol}...")
                    
                    page = await context.new_page()
                    # Surgical Search API with Browser Context
                    api_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={clean_symbol}"
                    
                    # Human Jitter (Crucial for Rate Limiting)
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    # Direct Request through Authenticated Browser Session to bypass Cloudflare/Akamai fingerprinting
                    # Use a dummy navigation or just fetch directly if session allows
                    # We 'prime' the session by going to yahoo home first if needed, but search often works direct
                    
                    try:
                        # Direct fetch within browser context inherits all stealth headers + session bits
                        content = await page.evaluate(f'async () => {{ const r = await fetch("{api_url}"); return r.json(); }}')
                    except Exception:
                        # Fallback: Navigate to the URL if fetch is blocked
                        await page.goto(api_url, wait_until="domcontentloaded")
                        raw = await page.locator("body").inner_text()
                        content = json.loads(raw)
                    
                    news_list = content.get("news", [])
                    processed = []
                    for item in news_list:
                        if not isinstance(item, dict):
                            continue
                        pub_time = item.get("providerPublishTime", 0)
                        if pub_time < cutoff_ts:
                            continue # Filter 7-day lookback

                        title = item.get("title", "No Title")
                        
                        # Anti-Spam Filter: Ensure the article is actually about the ticker
                        related = item.get("relatedTickers")
                        if related is not None:
                            if clean_symbol.upper() not in [r.upper() for r in related]:
                                continue
                        else:
                            # If no related tickers, enforce strict text matching to prevent Yahoo default spam
                            if clean_symbol.upper() not in title.upper():
                                continue

                        processed.append({
                            "title": title,
                            "link": item.get("link", ""),
                            "provider": item.get("publisher", "Yahoo"),
                            "date": pub_time,
                            "vibe_score": self.get_vibe(title)
                        })
                    master_news[symbol] = processed[:15]
                    await page.close()
                    
                except Exception as e:
                    print(f"[ERR] Failed {symbol}: {e}")
                    master_news[symbol] = []
                    
            await browser.close()
        return master_news

if __name__ == "__main__":
    # Internal CLI Test
    async def test():
        fetcher = YahooNewsFetcher()
        test_data = await fetcher.fetch_batch(["NVDA", "AAOI"])
        print(f"Results: {json.dumps(test_data, indent=2)}")
    
    asyncio.run(test())
