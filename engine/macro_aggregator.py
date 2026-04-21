import feedparser
import time
import json
import asyncio
import logging
import random
from pathlib import Path
from curl_cffi import requests
from datetime import datetime, timezone, timedelta

# V23.60: Macro Aggregator for GIGACPO Cockpit
# High-density filtration of tech/semi/photonics intelligence.

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
LIVE_PRICES_JSON = ROOT / 'database' / 'live_prices.json'

class MacroAggregator:
    def __init__(self):
        self.priority_keywords = [
            "PHOTONICS", "SEMI", "CXL", "BLACKWELL", "NVIDIA", "SUPPLY CHAIN", 
            "CHIP", "AI REVENUE", "WAFER", "HBM", "CPO", "SILICON"
        ]
        self.priority_tickers = [
            "NVDA", "AMD", "AVGO", "ALAB", "ARM", "MRVL", "LITE", "FN", 
            "COHR", "LUNA", "PII", "RMBS", "INTC", "TSM", "HIVE"
        ]
        self.feeds = {
            "MarketWatch Pulse": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
            "Investing Tech": "https://www.investing.com/rss/news_25.rss",
            "Investing World": "https://www.investing.com/rss/news_301.rss",
            "CNBC Tech": "https://www.cnbc.com/id/19854910/device/rss/rss.html"
        }

    def _load_prices(self):
        if not LIVE_PRICES_JSON.exists():
            return {}
        try:
            with open(LIVE_PRICES_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def score_headline(self, title):
        """Calculates 'Intel Significance' based on tech/semi focus."""
        score = 10
        t_upper = title.upper()
        
        # Keyword bonuses
        for kw in self.priority_keywords:
            if kw in t_upper:
                score += 50
        
        # Ticker bonuses (if ticker is in title)
        for tick in self.priority_tickers:
            if f" {tick} " in f" {t_upper} " or tick + " " in t_upper or "(" + tick in t_upper:
                score += 100 # High priority for our core tech watchlist
        
        return score

    def enrich_headline(self, title, prices):
        """Appends real-time price info if a known ticker is detected."""
        enriched = title
        detected_ticker = None
        
        # Check title for tickers in our priority list
        for tick in self.priority_tickers:
            if tick in title.upper():
                detected_ticker = tick
                break
        
        if detected_ticker and detected_ticker in prices:
            p_data = prices[detected_ticker]
            if p_data.get('price'):
                p = p_data['price']
                chg = p_data.get('change_pct', 0)
                color = "green" if chg >= 0 else "red"
                sign = "+" if chg >= 0 else ""
                enriched = f"<strong>{detected_ticker}</strong> (${p:.2f} {sign}{chg:.1f}%): {title}"
        
        return enriched

    async def fetch_agg(self):
        """Aggregates and scores news from all feeds."""
        log.info("[MACRO] Aggregating multi-source news feeds...")
        all_items = []
        prices = self._load_prices()
        
        for name, url in self.feeds.items():
            try:
                log.info(f"  Fetching {name}...")
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')
                    pub_date = entry.get('published', '')
                    
                    score = self.score_headline(title)
                    enriched_title = self.enrich_headline(title, prices)
                    
                    all_items.append({
                        "title": enriched_title,
                        "raw_title": title,
                        "link": link,
                        "source": name,
                        "score": score,
                        "date": pub_date
                    })
            except Exception as e:
                log.error(f"  Error fetching {name}: {e}")

        # Sort by score (descending) and take top 15
        top_15 = sorted(all_items, key=lambda x: x['score'], reverse=True)[:15]
        log.info(f"[MACRO] Aggregation complete. {len(top_15)} high-alpha headlines identified.")
        return top_15

if __name__ == "__main__":
    async def test():
        agg = MacroAggregator()
        results = await agg.fetch_agg()
        for i, res in enumerate(results):
            print(f"{i+1}. [{res['score']}] {res['title']}")
            
    asyncio.run(test())
