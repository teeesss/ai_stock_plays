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
VELOCITY_PULSE_DB = ROOT / 'database' / 'macro_velocity_metrics.json'

class MacroAggregator:
    def __init__(self):
        self.velocity_pulse = {} # Tracks keyword frequency rolling window
        self.priority_keywords = [
            "PHOTONICS", "SEMI", "CXL", "BLACKWELL", "NVIDIA", "SUPPLY CHAIN", 
            "CHIP", "AI REVENUE", "WAFER", "HBM", "CPO", "SILICON",
            "MARKET OVERVIEW", "WALL ST", "CLOSING BELL", "OPENING BELL", "RECAP", "STOCKS FALL", "STOCKS RISE",
            "CRUDE", "OIL", "CEASEFIRE", "GEOPOLITICAL", "DEFENSE", "ENERGY", "HORMUZ", "OPEC", "BRENT",
            "EARNINGS", "PROFIT", "QUARTERLY", "REVENUE", "GUIDANCE"
        ]
        self.priority_tickers = [
            "NVDA", "AMD", "AVGO", "ALAB", "ARM", "MRVL", "LITE", "FN", 
            "COHR", "LUNA", "PII", "RMBS", "INTC", "TSM", "HIVE"
        ]
        # V24.1: Hardened 15 High-Fidelity Sources (Updated with working URLs)
        self.feeds = {
            "WSJ Markets": {"url": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain", "type": "rss", "weight": 150},
            "CNBC Top News": {"url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "type": "rss", "weight": 140},
            "CNBC World": {"url": "https://www.cnbc.com/id/100727362/device/rss/rss.html", "type": "rss", "weight": 130},
            "IBD Market News": {"url": "https://www.investors.com/rss.axd?path=InvestingRSS.xml", "type": "rss", "weight": 120},
            "CNBC Markets": {"url": "https://www.cnbc.com/id/10000664/device/rss/rss.html", "type": "rss", "weight": 110},
            "MarketWatch Pulse": {"url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse", "type": "rss", "weight": 100},
            "Seeking Alpha": {"url": "https://seekingalpha.com/feed.xml", "type": "rss", "weight": 90},
            "Business Insider": {"url": "https://markets.businessinsider.com/rss/news", "type": "rss", "weight": 80},
            "CNBC Earnings": {"url": "https://www.cnbc.com/id/15839135/device/rss/rss.html", "type": "rss", "weight": 170},
            "Yahoo Finance Tech": {"url": "https://finance.yahoo.com/topic/tech/", "type": "scrape", "weight": 60},
            "CNBC Tech": {"url": "https://www.cnbc.com/id/19854910/device/rss/rss.html", "type": "rss", "weight": 50},
            "OilPrice Macro": {"url": "https://oilprice.com/feed/rss.html", "type": "rss", "weight": 115},
            "CNBC Energy": {"url": "https://www.cnbc.com/id/19836768/device/rss/rss.html", "type": "rss", "weight": 35},
            "ZeroHedge": {"url": "http://feeds.feedburner.com/zerohedge/feed", "type": "rss", "weight": 20},
            "Investing Tech": {"url": "https://www.investing.com/rss/news_25.rss", "type": "rss", "weight": 10}
        }
        self.blacklist = ["DAVE RAMSEY", "PR NEWSWIRE", "BUSINESS WIRE", "GLOBE NEWSWIRE"]

    def _load_prices(self):
        if not LIVE_PRICES_JSON.exists():
            return {}
        try:
            with open(LIVE_PRICES_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def score_headline(self, title, source_name):
        """Calculates 'Intel Significance' based on tech/semi focus and source weight."""
        t_upper = title.upper()
        
        # Blacklist enforcement
        for bl in self.blacklist:
            if bl in t_upper:
                return -1000
        
        # Base weight from source
        score = self.feeds.get(source_name, {}).get("weight", 10)
        
        # Keyword bonuses
        for kw in self.priority_keywords:
            if kw in t_upper:
                score += 50
        
        # Market Overview / Macro Anchor bonuses
        anchor_words = ["MARKET OVERVIEW", "WALL ST", "CLOSING BELL", "OPENING BELL", "RECAP", "STOCKS FALL", "STOCKS RISE", "STOCK MARKET TODAY"]
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

    def _update_velocity_pulse(self, title, now_ts):
        """V24.2 SVM: Tracks frequency of keywords to identify velocity shifts."""
        t_upper = title.upper()
        for kw in self.priority_keywords:
            if kw in t_upper:
                if kw not in self.velocity_pulse: self.velocity_pulse[kw] = []
                self.velocity_pulse[kw].append(now_ts)
        
        for tick in self.priority_tickers:
            if re.search(rf'\b{tick}\b', t_upper):
                if tick not in self.velocity_pulse: self.velocity_pulse[tick] = []
                self.velocity_pulse[tick].append(now_ts)

    def _finalize_velocity_metrics(self):
        """Calculates deltas (velocity) for monitored keywords over the last 4h vs prior 24h."""
        now = time.time()
        metrics = {}
        for kw, timestamps in self.velocity_pulse.items():
            # Clean old timestamps (> 24h)
            valid = [ts for ts in timestamps if (now - ts) < 86400]
            self.velocity_pulse[kw] = valid
            
            recent_4h = [ts for ts in valid if (now - ts) < 14400]
            prior_20h = [ts for ts in valid if 14400 <= (now - ts) < 86400]
            
            # Simple Velocity: Frequency ratio
            v_score = len(recent_4h) / (len(prior_20h)/5 + 1) # Normalized
            metrics[kw] = {
                "count_24h": len(valid),
                "count_4h": len(recent_4h),
                "velocity": round(v_score, 2)
            }
        
        try:
            with open(VELOCITY_PULSE_DB, 'w', encoding='utf-8') as f:
                json.dump({"timestamp": now, "metrics": metrics}, f, indent=4)
        except: pass
        return metrics

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
            for name, cfg in self.feeds.items():
                url = cfg["url"]
                domain = urllib.parse.urlparse(url).netloc
                if domain not in domain_queues:
                    domain_queues[domain] = []
                domain_queues[domain].append((name, cfg))

            async def process_queue(domain, queue):
                queue_items = []
                for i, (name, cfg) in enumerate(queue):
                    url = cfg["url"]
                    f_type = cfg["type"]
                    try:
                        # Jitter ONLY within the same domain (V23.79 Optimization)
                        if i > 0:
                            delay = random.uniform(2.5, 7.0)
                            log.info(f"  [STEALTH] Cadence Match ({domain}): Sleeping {delay:.2f}s...")
                            await asyncio.sleep(delay)

                        log.info(f"  [FETCH] {name} ({f_type.upper()}) -> {url}")

                        # V24.2: Robust Fetch with Retry & Impersonation Rotation
                        res = None
                        impersonations = ["chrome110", "chrome120", "chrome124", "edge101", "safari_ios_16_5"]
                        
                        for attempt in range(3):
                            try:
                                current_imp = impersonations[attempt % len(impersonations)]
                                res = await client.get(url, timeout=15, impersonate=current_imp)
                                if res.status_code == 200: 
                                    break
                                log.warning(f"  [!] Attempt {attempt+1} failed ({res.status_code}) for {name}. Retrying with {current_imp}...")
                                await asyncio.sleep(random.uniform(2, 5))
                            except Exception as e:
                                log.error(f"  [!] Fetch error {name} (Attempt {attempt+1}): {e}")
                                await asyncio.sleep(2)

                        if not res or res.status_code != 200:
                            status = res.status_code if res else "TIMEOUT"
                            log.error(f"  [!] Blocked or Error {name}: HTTP {status}")
                            continue

                        now_ts = time.time()
                        source_item_count = 0
                        
                        if f_type == "rss":
                            feed = feedparser.parse(res.content)
                            for entry in feed.entries:
                                title = entry.get('title', 'No Title').strip()
                                
                                # V24.1: Hardened Deduplication (Jaccard-lite)
                                tokens = frozenset(re.findall(r'\b\w{4,}\b', title.lower()))
                                is_dup = False
                                for st in seen_titles:
                                    overlap = len(tokens & st) / (len(tokens | st) + 1)
                                    if overlap > 0.4: is_dup = True; break
                                if is_dup: continue
                                seen_titles.add(tokens)

                                link = entry.get('link', '')
                                pub_date = entry.get('published', '')
                                
                                entry_ts = now_ts
                                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                    entry_ts = time.mktime(entry.published_parsed)
                                    if (now_ts - entry_ts) > (48 * 3600):
                                        continue
                                
                                score = self.score_headline(title, name)
                                if score < 0: continue
                                
                                # Flag Earnings (V24.1)
                                is_earnings = "EARNINGS" in title.upper() or name == "CNBC Earnings"
                                if is_earnings: score += 100 # Boost earnings
                                
                                enriched_title = self.enrich_headline(title, prices)
                                
                                summary = entry.get('summary', entry.get('description', ''))
                                summary = re.sub(r'<[^>]+>', '', summary).strip()
                                summary = re.sub(r'(?i)[T]?he post .*? appeared first on .*?(?:\.|$)', '', summary).strip()
                                summary = re.sub(r'(?i)Read more on Yahoo Finance.*', '', summary).strip()
                                
                                # V24.2: Signal Decay Engine (5% per hour after 1h, floor at 50%)
                                hours_old = (now_ts - entry_ts) / 3600
                                decay = max(0.5, 1.0 - (max(0, hours_old - 1) * 0.05))
                                score = score * decay
                                
                                # V24.2: Sentiment Velocity Monitor (SVM) Update
                                self._update_velocity_pulse(title, now_ts)
                                
                                queue_items.append({
                                    "title": enriched_title,
                                    "raw_title": title,
                                    "summary": summary,
                                    "link": link,
                                    "source": name,
                                    "score": round(score, 1),
                                    "date": pub_date,
                                    "is_earnings": is_earnings
                                })
                                source_item_count += 1
                        else:
                            # Scrape Type
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(res.content, 'html.parser')
                            
                            items = []
                            if "bloomberg" in url:
                                links = soup.find_all('a', href=re.compile(r'/news/articles/|/news/features/'))
                                for l in links[:10]:
                                    title = l.get_text().strip()
                                    if len(title) < 20: continue
                                    items.append({"title": title, "link": "https://www.bloomberg.com" + l['href'] if l['href'].startswith('/') else l['href']})
                            elif "thefly" in url:
                                links = soup.find_all('a', class_='newsTitleLink')
                                for l in links[:10]:
                                    title = l.get_text().strip()
                                    items.append({"title": title, "link": "https://thefly.com" + l['href'] if l['href'].startswith('/') else l['href']})
                            elif "yahoo" in url:
                                links = soup.find_all('a', class_='subLink') or soup.find_all('h3')
                                for l in links[:10]:
                                    title = l.get_text().strip()
                                    a_tag = l if l.name == 'a' else l.find('a')
                                    if a_tag and a_tag.get('href'):
                                        items.append({"title": title, "link": a_tag['href']})

                            for it in items:
                                title = it['title']
                                tokens = frozenset(re.findall(r'\b\w{4,}\b', title.lower()))
                                is_dup = False
                                for st in seen_titles:
                                    overlap = len(tokens & st) / (len(tokens | st) + 1)
                                    if overlap > 0.4: is_dup = True; break
                                if is_dup: continue
                                seen_titles.add(tokens)
                                
                                score = self.score_headline(title, name)
                                if score < 0: continue
                                
                                # Flag Earnings (V24.1)
                                is_earnings = "EARNINGS" in title.upper() or name == "CNBC Earnings"
                                if is_earnings: score += 100 # Boost earnings

                                enriched_title = self.enrich_headline(title, prices)
                                
                                # V24.2: SVM Update
                                self._update_velocity_pulse(title, now_ts)
                                
                                queue_items.append({
                                    "title": enriched_title,
                                    "raw_title": title,
                                    "summary": "",
                                    "link": it['link'],
                                    "source": name,
                                    "score": score,
                                    "date": "Just now",
                                    "is_earnings": is_earnings
                                })
                                source_item_count += 1
                        
                        log.info(f"  [SUCCESS] {name}: {source_item_count} items identified.")
                    except Exception as e:
                        log.error(f"  [ERR] Failed {name}: {e}")
                return queue_items

            # Execute all domain groups in parallel
            tasks = [process_queue(domain, q) for domain, q in domain_queues.items()]
            results_batches = await asyncio.gather(*tasks)
            for batch in results_batches:
                all_items.extend(batch)

        # V24.1: Dynamic List Extension for Earnings News
        has_earnings = any(it.get('is_earnings') for it in all_items)
        limit = 45 # Give plenty of buffer to ensure 15 non-earnings and some earnings
        
        # Sort by score (descending) and take top limit
        top_ranked = sorted(all_items, key=lambda x: x['score'], reverse=True)[:limit]
        
        # Save to Cache
        try:
            with open(MACRO_NEWS_CACHE, 'w', encoding='utf-8') as f:
                json.dump({"timestamp": time.time(), "headlines": top_ranked}, f, indent=4)
        except: pass

        # V24.2: Finalize Sentiment Velocity Metrics (SVM)
        self._finalize_velocity_metrics()

        log.info(f"[MACRO] Aggregation complete. {len(top_ranked)} high-alpha headlines identified (Earnings Boost: {has_earnings}).")
        return top_ranked

if __name__ == "__main__":
    async def test():
        agg = MacroAggregator()
        results = await agg.fetch_agg()
        for i, res in enumerate(results):
            print(f"{i+1}. [{res['score']}] {res['title']}")
            
    asyncio.run(test())
