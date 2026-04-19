
import asyncio
import random
import json
import time
import sys, os
from curl_cffi import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from yahoo_auth import get_valid_auth

class YahooNewsFetcher:
    """Refactored News Fetcher: Decoupled Extraction using curl_cffi and Auth Caching."""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def get_vibe(self, text):
        """Calculates VADER sentiment score."""
        return self.analyzer.polarity_scores(text)['compound']

    async def fetch_batch(self, tickers, days=7):
        """Fetches news with 2026-grade stealth. Filtering by age."""
        master_news = {}
        cutoff_ts = int(time.time()) - (days * 86400)
        
        # Retrieve Valid/Cached Authenticated Session
        cookie_dict, crumb, user_agent = await get_valid_auth()
        
        client = requests.Session(impersonate='chrome146')
        client.headers.update({
            'User-Agent': user_agent,
            'Accept': '*/*',
            'Referer': 'https://finance.yahoo.com/'
        })
        client.cookies.update(cookie_dict)
        
        for i, symbol in enumerate(tickers):
            try:
                clean_symbol = symbol.strip().replace("$", "").split(" / ")[0]
                print(f"[STEALTH] Yahoo News Sync: {clean_symbol}... ({i+1}/{len(tickers)})")
                
                # Surgical Search API with Browser Context
                api_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={clean_symbol}"
                
                # Randomized Stealth Jitter (3.3 - 10s as per specs)
                if i > 0:
                    delay = random.uniform(3.3, 10.0)
                    print(f"  [WAIT] Sleeping {delay:.2f}s to mimic human browsing...")
                    await asyncio.sleep(delay)
                
                res = client.get(api_url, timeout=12)
                if res.status_code != 200:
                    print(f"  [!] Failed to fetch news for {clean_symbol}: HTTP {res.status_code}")
                    master_news[symbol] = []
                    continue
                    
                content = res.json()
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
                
            except Exception as e:
                print(f"[ERR] Failed {symbol}: {e}")
                master_news[symbol] = []
                    
        return master_news

if __name__ == "__main__":
    # Internal CLI Test
    async def test():
        fetcher = YahooNewsFetcher()
        test_data = await fetcher.fetch_batch(["NVDA", "AAOI"])
        print(f"Results: {json.dumps(test_data, indent=2)}")
    
    asyncio.run(test())
