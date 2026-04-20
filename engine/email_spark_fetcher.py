"""
engine/email_spark_fetcher.py
============================
Sidecar data fetcher for the GIGACPO Email System.
Fetches 15m interval chart data for sparkline generation.
Does NOT affect primary live_prices.py logic or production terminal state.
"""

import json
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from curl_cffi import requests

# Import auth and config from primary engine
import sys
sys.path.append(str(Path(__file__).parent))
from yahoo_auth import get_valid_auth

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger("email_spark")

ROOT = Path(__file__).parent.parent
OUT_JSON = ROOT / 'database' / 'email_sparklines.json'

async def fetch_sparkline(symbol: str, client, crumb: str):
    """Fetches 1-day chart data with 15m intervals."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=15m&range=1d&crumb={crumb}"
    
    try:
        res = client.get(url, timeout=10)
        if res.status_code != 200:
            return None
            
        data = res.json()
        chart = data.get('chart', {}).get('result', [{}])[0]
        indicators = chart.get('indicators', {}).get('adjclose', [{}])[0]
        closes = indicators.get('adjclose', [])
        
        # Filter out None values and return a compact set of points (max 30)
        valid_points = [p for p in closes if p is not None]
        if not valid_points: return None
        
        # Sub-sample to ~24 points for clean rendering
        step = max(1, len(valid_points) // 24)
        return valid_points[::step]
        
    except Exception as e:
        log.error(f"Error fetching spark for {symbol}: {e}")
        return None

async def run_spark_fetch(tickers: list[str]):
    """Main entry point for email system to refresh spark data."""
    log.info(f"Refreshing sparklines for {len(tickers)} tickers...")
    
    cookie_dict, crumb, user_agent = await get_valid_auth()
    client = requests.Session(impersonate='chrome146')
    client.headers.update({'User-Agent': user_agent})
    client.cookies.update(cookie_dict)
    
    results = {}
    for t in tickers:
        points = await fetch_sparkline(t, client, crumb)
        if points:
            results[t] = points
            log.info(f"  Captured {len(points)} points for {t}")
            
    # Save to isolated JSON
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f)
    log.info(f"Sparklines saved to {OUT_JSON}")
    return results

if __name__ == "__main__":
    # Test run with sample tickers
    asyncio.run(run_spark_fetch(["AAPL", "TSLA", "MRVL", "BTC-USD"]))
