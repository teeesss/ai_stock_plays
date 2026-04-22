import feedparser
import time
import json
import asyncio
import logging
import random
from pathlib import Path
from curl_cffi import requests
from datetime import datetime, timezone, timedelta
import re

# V23.60: Macro Aggregator for GIGACPO Cockpit
# High-density filtration of tech/semi/photonics intelligence.
import urllib.parse
from curl_cffi.requests import AsyncSession

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
LIVE_PRICES_JSON = ROOT / 'database' / 'live_prices.json'
MACRO_NEWS_CACHE = ROOT / 'database' / 'macro_news_cache.json'

class MacroAggregator:
    def __init__(self):
        self.priority_keywords = [
            "PHOTONICS", "SEMI", "CXL", "BLACKWELL", "NVIDIA", "SUPPLY CHAIN", 
            "CHIP", "AI REVENUE", "WAFER", "HBM", "CPO", "SILICON",
            "MARKET OVERVIEW", "WALL ST", "CLOSING BELL", "OPENING BELL", "RECAP", "STOCKS FALL", "STOCKS RISE"
        ]
        self.priority_tickers = [
            "NVDA", "AMD", "AVGO", "ALAB", "ARM", "MRVL", "LITE", "FN", 
            "COHR", "LUNA", "PII", "RMBS", "INTC", "TSM", "HIVE"
        ]
        self.feeds = {
            "CNBC Top News": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
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
        
        # Market Overview / Macro Anchor bonuses
        anchor_words = ["MARKET OVERVIEW", "WALL ST", "CLOSING BELL", "OPENING BELL", "RECAP"]
        for aw in anchor_words:
            if aw in t_upper:
                score += 200
        
        return score

    def enrich_headline(self, title, prices):
        """Appends real-time price info if a known ticker is detected."""
        enriched = title
        detected_ticker = None
        
        import re
        for tick in self.priority_tickers:
            if re.search(rf'\b{tick}\b', title.upper()):
                detected_ticker = tick
                break
        
        if detected_ticker and detected_ticker in prices:
            p_data = prices[detected_ticker]
            if p_data.get('price'):
                p = p_data['price']
                chg = p_data.get('change_pct', 0)
                color = "green" if chg >= 0 else "red"
                sign = "+" if chg >= 0 else ""
                enriched = f"<strong>{detected_ticker}</strong>&nbsp;(${p:.2f}&nbsp;{sign}{chg:.1f}%):&nbsp;{title}"
        
        return enriched

    async def fetch_agg(self):
        """Aggregates and scores news with hardening/stealth protocols."""
        print(f"[DEBUG] fetch_agg called. Cache target: {MACRO_NEWS_CACHE}")
        # V23.61: 15-minute Cache Enforcement
        if MACRO_NEWS_CACHE.exists():
            try:
                with open(MACRO_NEWS_CACHE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    cached_at = cache_data.get("timestamp", 0)
                    elapsed = time.time() - cached_at
                    if elapsed < 900: # 15 minutes
                        ttl = int(900 - elapsed)
                        log.info(f"[CACHE] Macro News Fresh: {ttl}s remaining. Serving {len(cache_data.get('headlines', []))} ranked items.")
                        return cache_data.get("headlines", [])
                    else:
                        log.info(f"[CACHE] Macro News EXPIRED ({int(elapsed)}s old). Triggering fresh aggregate...")
            except Exception as e:
                log.warning(f"[CACHE] Read failure: {e}")

        log.info("[MACRO] Aggregating multi-source news feeds...")
        all_items = []
        prices = self._load_prices()
        
        # V23.60: Use centralized stealth auth for fingerprint matching
        try:
            from yahoo_auth import get_valid_auth
            _, _, user_agent = await get_valid_auth()
        except:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

        # V23.91: Strict Cross-Source Deduplication
        seen_titles = set()
        
        async with AsyncSession(impersonate='chrome146') as client:
            client.headers.update({
                'User-Agent': user_agent,
                'Accept': 'application/rss+xml, application/xml, text/xml, */*'
            })

            # V23.79: Parallelize across domains, sequential jitter within domains
            domain_queues = {}
            for name, url in self.feeds.items():
                domain = urllib.parse.urlparse(url).netloc
                if domain not in domain_queues:
                    domain_queues[domain] = []
                domain_queues[domain].append((name, url))

            async def process_queue(domain, queue):
                queue_items = []
                for i, (name, url) in enumerate(queue):
                    try:
                        # Jitter ONLY within the same domain (V23.79 Optimization)
                        if i > 0:
                            delay = random.uniform(3.3, 10.0)
                            log.info(f"  [STEALTH] Cadence Match ({domain}): Sleeping {delay:.2f}s...")
                            await asyncio.sleep(delay)

                        log.info(f"  [STEALTH] Fetching {name} Pulse...")
                        res = await client.get(url, timeout=15)
                        if res.status_code != 200:
                            log.error(f"  [!] Blocked or Error {name}: HTTP {res.status_code}")
                            continue

                        feed = feedparser.parse(res.content)
                        now_ts = time.time()
                        for entry in feed.entries:
                            title = entry.get('title', 'No Title').strip()
                            
                            # Deduplication Logic
                            norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
                            if norm_title in seen_titles: continue
                            seen_titles.add(norm_title)

                            link = entry.get('link', '')
                            pub_date = entry.get('published', '')
                            
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                entry_ts = time.mktime(entry.published_parsed)
                                if (now_ts - entry_ts) > (48 * 3600):
                                    continue
                            
                            score = self.score_headline(title)
                            enriched_title = self.enrich_headline(title, prices)
                            
                            summary = entry.get('summary', entry.get('description', ''))
                            summary = re.sub(r'<[^>]+>', '', summary).strip()
                            
                            queue_items.append({
                                "title": enriched_title,
                                "raw_title": title,
                                "summary": summary,
                                "link": link,
                                "source": name,
                                "score": score,
                                "date": pub_date
                            })
                    except Exception as e:
                        log.error(f"  [ERR] Failed {name}: {e}")
                return queue_items

            # Execute all domain groups in parallel
            tasks = [process_queue(domain, q) for domain, q in domain_queues.items()]
            results_batches = await asyncio.gather(*tasks)
            for batch in results_batches:
                all_items.extend(batch)

        # Sort by score (descending) and take top 15
        top_15 = sorted(all_items, key=lambda x: x['score'], reverse=True)[:15]
        
        # Save to Cache
        try:
            with open(MACRO_NEWS_CACHE, 'w', encoding='utf-8') as f:
                json.dump({"timestamp": time.time(), "headlines": top_15}, f, indent=4)
        except: pass

        log.info(f"[MACRO] Aggregation complete. {len(top_15)} high-alpha headlines identified.")
        return top_15

if __name__ == "__main__":
    async def test():
        agg = MacroAggregator()
        results = await agg.fetch_agg()
        for i, res in enumerate(results):
            print(f"{i+1}. [{res['score']}] {res['title']}")
            
    asyncio.run(test())
