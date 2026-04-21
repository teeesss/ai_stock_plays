# V23.59: Auto-Dependency Guardian
try:
    try:
        from dependency_mgr import ensure_dependencies
    except ImportError:
        from engine.dependency_mgr import ensure_dependencies
    ensure_dependencies()
except ImportError:
    pass

import argparse
import time
import asyncio
import os
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.news_fetcher import YahooNewsFetcher

MASTER_DATA = "database/CPO_MASTER_DATA.json"
NEWS_DB = "database/YAHOO_NEWS_DB.json"

FETCH_TTL_SECONDS = 3600  # 1 Hour Cooldown per ticker

def get_all_tickers():
    """Extracts all monitored tickers from master data."""
    if not os.path.exists(MASTER_DATA):
        print(f"[ERR] Master data missing: {MASTER_DATA}")
        return []
    try:
        with open(MASTER_DATA, "r", encoding='utf-8') as f:
            data = json.load(f)
        return list(data.keys())
    except Exception as e:
        print(f"[ERR] Failed to parse master data: {e}")
        return []

def load_news_db():
    if not os.path.exists(NEWS_DB):
        return {"last_updated": "", "ticker_meta": {}, "news": {}}
    try:
        with open(NEWS_DB, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"last_updated": "", "ticker_meta": {}, "news": {}}

async def run_sync():
    """Main orchestration for ALL Yahoo News sync with TTL Caching."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force fetch regardless of cache")
    args = parser.parse_args()

    print("============================================================")
    print(f"YAHOO NEWS UNIVERSE SYNC (V16.7) - {datetime.now().isoformat()}")
    if args.force: print("[!] FORCE MODE ENABLED")
    print("============================================================")
    
    all_tickers = get_all_tickers()
    if not all_tickers:
        print("[ERR] No tickers found for sync.")
        return

    db = load_news_db()
    current_news = db.get("news", {})
    ticker_meta = db.get("ticker_meta", {})
    
    now_ts = time.time()
    tickers_to_fetch = []
    
    for t in all_tickers:
        last_fetch = ticker_meta.get(t, {}).get("last_fetch", 0)
        if args.force or (now_ts - last_fetch > FETCH_TTL_SECONDS):
            tickers_to_fetch.append(t)

    if not tickers_to_fetch:
        print("[SUCCESS] All tickers were fresh. No remote calls needed.")
        return

    print(f"[INFO] Syncing {len(tickers_to_fetch)} monitored assets (7-day lookback)...")
    
    fetcher = YahooNewsFetcher()
    fresh_results = await fetcher.fetch_batch(tickers_to_fetch, days=7)
    
    for ticker, articles in fresh_results.items():
        if ticker not in current_news:
            current_news[ticker] = articles
        else:
            existing_titles = {a['title'] for a in current_news[ticker]}
            new_articles = [a for a in articles if a['title'] not in existing_titles]
            current_news[ticker] = new_articles + current_news[ticker]
            current_news[ticker] = current_news[ticker][:15]
        
        ticker_meta[ticker] = {
            "last_fetch": now_ts,
            "fetch_date": datetime.now().isoformat()
        }
    
    try:
        with open(NEWS_DB, "w", encoding='utf-8') as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "ticker_meta": ticker_meta,
                "news": current_news
            }, f, indent=4)
        print(f"[SUCCESS] News DB updated. Total universe coverage: {len(all_tickers)}")
    except Exception as e:
        print(f"[ERR] Failed to save news database: {e}")

    # Rebuild flat YAHOO_NEWS_MODULE.js for dashboard
    _rebuild_news_module(current_news)

def _rebuild_news_module(news: dict):
    """Flatten ticker-keyed news into articles array for dashboard consumption."""
    from datetime import timezone
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUT_JS = os.path.join(ROOT, 'database', 'YAHOO_NEWS_MODULE.js')
    seen_ids = set()
    flat = []
    for ticker, articles in news.items():
        for a in articles:
            key = a.get('link') or a.get('url') or ''
            if key and key in seen_ids:
                for ex in flat:
                    if ex.get('url') == key:
                        if ticker not in ex['tickers']:
                            ex['tickers'].append(ticker)
                continue
            seen_ids.add(key)
            raw = a.get('date') or a.get('published') or 0
            if isinstance(raw, (int, float)) and raw > 1_000_000_000:
                from datetime import datetime, timezone
                pub = datetime.fromtimestamp(raw, tz=timezone.utc).strftime('%Y-%m-%d %H:%M EST')
            else:
                pub = str(raw)[:16] if raw else ''
            flat.append({
                'title': a.get('title', ''),
                'url':   a.get('link') or a.get('url') or '',
                'source': a.get('provider') or a.get('source') or '',
                'summary': a.get('summary') or '',
                'published_est': pub,
                'tickers': [ticker],
                'vibe_score': a.get('vibe_score', 0),
            })
    flat.sort(key=lambda x: x['published_est'], reverse=True)
    payload = {'last_updated': datetime.now().isoformat(), 'total': len(flat), 'articles': flat}
    js = 'window.YAHOO_NEWS_MODULE = ' + json.dumps(payload, ensure_ascii=True) + ';'
    with open(OUT_JS, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f"[SUCCESS] YAHOO_NEWS_MODULE.js rebuilt: {len(flat)} articles")

if __name__ == "__main__":
    asyncio.run(run_sync())