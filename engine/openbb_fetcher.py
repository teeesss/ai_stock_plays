
"""
engine/openbb_fetcher.py
========================
OpenBB v4 supplemental data fetcher for GIGACPO terminal.
Refactored to use decoupled yahoo_auth (curl_cffi) to prevent bans.
"""

import json
import time
import logging
import asyncio
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure we can import sibling engine modules when run from root
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from curl_cffi import requests
from yahoo_auth import get_valid_auth

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'database' / 'CPO_MASTER_DATA.json'
JS_PATH = ROOT / 'database' / 'dashboard_data.js'

SKIP_TICKERS = {'AYAR', 'RANV', 'CelestialAI', 'SCINTIL', 'PTF', 'LADR', 'XSD'}

def clean_ticker(ticker: str) -> str:
    """Extract primary ticker from compound 'A.XX / B' format."""
    return ticker.split(' / ')[0].strip()

async def _get_yf_supplement_stealth(ticker_symbol: str, entry: dict, client, crumb) -> dict:
    """
    Fetches analyst stats and 1Y history using decoupled stealth session.
    """
    result = {}
    primary = clean_ticker(ticker_symbol)
    
    # 1. Historical Data (for 1y Return & 7d Momentum)
    # Endpoint: v8/finance/chart
    chart_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{primary}?range=1y&interval=1d&includePrePost=false&crumb={crumb}"
    
    try:
        resp = client.get(chart_url, timeout=12)
        if resp.status_code == 200:
            data = resp.json().get('chart', {}).get('result', [{}])[0]
            if data:
                timestamps = data.get('timestamp', [])
                quotes = data.get('indicators', {}).get('quote', [{}])[0].get('close', [])
                
                # Filter None prices
                valid_points = []
                for t, p in zip(timestamps, quotes):
                    if p is not None: valid_points.append(p)
                
                if len(valid_points) > 2:
                    # 1y Return
                    start_p = valid_points[0]
                    end_p = valid_points[-1]
                    perf_1y = round(((end_p / start_p) - 1) * 100, 1)
                    result['perf_1y'] = perf_1y
                    
                    # Recent Action (Last 7 bars)
                    recent_prices = valid_points[-8:]
                    status = []
                    for i in range(1, len(recent_prices)):
                        status.append(1 if recent_prices[i] >= recent_prices[i-1] else 0)
                    while len(status) < 7: status.insert(0, 0)
                    result['recent_7d_status'] = status[-7:]
                    
    except Exception as e:
        log.warning(f"  {ticker_symbol}: Chart fetch failed: {e}")

    # 2. Extract Analyst Stats from financials blob (already in JSON)
    try:
        fin = entry.get('financials', {})
        fin_data = fin.get('financialData', {})
        stats = fin.get('defaultKeyStatistics', {})
        summary = fin.get('summaryDetail', {})

        def get_raw(obj, key):
            if not obj or not isinstance(obj, dict): return None
            val = obj.get(key)
            if hasattr(val, 'get'): return val.get('raw')
            return val

        target_mean = get_raw(fin_data, 'targetMeanPrice')
        target_high = get_raw(fin_data, 'targetHighPrice')
        target_low  = get_raw(fin_data, 'targetLowPrice')
        n_analysts  = get_raw(fin_data, 'numberOfAnalystOpinions')
        rec_mean    = get_raw(fin_data, 'recommendationMean')  
        inst_pct    = get_raw(stats, 'heldPercentInstitutions')
        short_pct   = get_raw(stats, 'shortPercentOfFloat')
        current_price = get_raw(fin_data, 'currentPrice') or get_raw(summary, 'regularMarketPrice')

        buy_pct = None
        if rec_mean is not None:
            if rec_mean <= 1.5:   buy_pct = 90
            elif rec_mean <= 2.0: buy_pct = 70
            elif rec_mean <= 2.5: buy_pct = 55
            elif rec_mean <= 3.0: buy_pct = 30
            else:                 buy_pct = 10

        if target_mean and current_price:
            implied_upside = round(((target_mean / current_price) - 1) * 100, 1)
            result['analyst_implied_upside_pct'] = implied_upside

        if target_mean is not None: result['analyst_target_mean'] = round(target_mean, 2)
        if target_high is not None: result['analyst_target_high'] = round(target_high, 2)
        if target_low  is not None: result['analyst_target_low']  = round(target_low, 2)
        if n_analysts  is not None: result['analyst_count']       = int(n_analysts)
        if buy_pct     is not None: result['analyst_buy_pct']     = buy_pct
        if rec_mean    is not None: result['rec_mean_raw']        = round(rec_mean, 2)
        if inst_pct    is not None: result['inst_ownership_pct']  = round(inst_pct * 100, 1)
        if short_pct   is not None: result['short_interest_pct']  = round(short_pct * 100, 1)

    except Exception as ex:
        log.debug(f"  {ticker_symbol}: Financials extraction skip: {ex}")

    return result

async def run_fetch_async(tickers: list = None, force: bool = False, dry_run: bool = False):
    with open(DB_PATH, encoding='utf-8') as f:
        data = json.load(f)

    if tickers is None:
        tickers = [t for t, e in data.items()
                   if e.get('human_research', {}).get('Bucket') != 'Private'
                   and t not in SKIP_TICKERS]

    log.info(f'OpenBB Supplement Fetcher — {len(tickers)} tickers')
    
    # Retrieve Valid/Cached Authenticated Session
    cookie_dict, crumb, user_agent = await get_valid_auth()
    
    client = requests.Session(impersonate='chrome146')
    client.headers.update({
        'User-Agent': user_agent,
        'Accept': '*/*',
        'Referer': 'https://finance.yahoo.com/'
    })
    client.cookies.update(cookie_dict)

    updated = 0
    skipped = 0

    for i, ticker in enumerate(tickers):
        if ticker not in data:
            skipped += 1
            continue

        entry = data[ticker]
        h = entry.get('human_research', {})
        
        # Skip if already fresh and not forcing
        existing = h.get('openbb_supplement', {})
        if existing and not force:
            skipped += 1
            continue

        log.info(f'[{i+1}/{len(tickers)}] Supplementing {ticker}...')
        
        # Stealth Throttling (3.3 - 10s as per specs)
        if i > 0:
            delay = random.uniform(3.3, 10.0)
            await asyncio.sleep(delay)

        supplement = await _get_yf_supplement_stealth(ticker, entry, client, crumb)

        if supplement:
            supplement['last_updated'] = datetime.now(timezone.utc).isoformat()
            if not dry_run:
                data[ticker]['human_research']['openbb_supplement'] = supplement
            updated += 1
            log.info(f"  -> {ticker}: 1y={supplement.get('perf_1y')}% | analysts={supplement.get('analyst_count')}")
        else:
            skipped += 1

        # Periodic checkpoint
        if updated > 0 and updated % 10 == 0:
            if not dry_run:
                with open(DB_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)

    if not dry_run and updated > 0:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        # Sync JS
        with open(JS_PATH, 'w', encoding='utf-8') as f:
            f.write('window.CPO_MASTER_DATA = ')
            json.dump(data, f, indent=2)
            f.write(';')
            
    log.info(f'Complete: {updated} updated, {skipped} skipped')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='GIGACPO OpenBB Supplement Fetcher')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers')
    parser.add_argument('--force', action='store_true', help='Re-fetch')
    parser.add_argument('--dry-run', action='store_true', help='No save')
    args = parser.parse_args()
    
    asyncio.run(run_fetch_async(tickers=args.tickers, force=args.force, dry_run=args.dry_run))
