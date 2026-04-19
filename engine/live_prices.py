"""
engine/live_prices.py
======================
Real-time price fetcher for the GIGACPO terminal.

Refactored to use StealthNavigator + curl_cffi directly, completely 
avoiding the unstable yfinance module and its 401 Unauthorized errors 
caused by Yahoo's 2026-grade anti-bot protections.

OUTPUT: database/live_prices.js
  window.LIVE_PRICES = {
    "CRDO":    { price: 28.5, change_pct: 2.3, volume: 1234567, updated: "2026-04-12T..." },
    "_meta":   { refreshed_at: "2026-04-12T17:30:00Z", total_tickers: 113,
                 top_gainers: [...], top_losers: [...], volume_spikes: [...] }
  };
"""

import json
import time
import logging
import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests
from yahoo_auth import get_valid_auth
import random

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'database' / 'CPO_MASTER_DATA.json'
OUT_JS  = ROOT / 'database' / 'live_prices.js'
OUT_JSON = ROOT / 'database' / 'live_prices.json'

# Skip private/non-tradable tickers
SKIP_TICKERS = {'AYAR', 'RANV', 'CelestialAI', 'SCINTIL'}

BATCH_SIZE = 10

def load_tickers() -> list[str]:
    """Load all public (non-private) tickers from the master database."""
    with open(DB_PATH, encoding='utf-8') as f:
        data = json.load(f)
    return [t for t, e in data.items()
            if e.get('human_research', {}).get('Bucket') != 'Private'
            and t not in SKIP_TICKERS]

def clean_ticker(ticker: str) -> str:
    """Extract primary ticker from compound 'A.XX / B' format."""
    return ticker.split(' / ')[0].strip()

def get_exchange_abbr(exchange: str) -> str:
    """Standardizes exchange names into clean abbreviations."""
    if not exchange: return "???"
    
    mapping = {
        "NasdaqGS": "NASDAQ",
        "NasdaqGM": "NASDAQ",
        "NasdaqCM": "NASDAQ",
        "Nasdaq":   "NASDAQ",
        "NMS":      "NASDAQ",
        "National Market System": "NASDAQ",
        "New York Stock Exchange": "NYSE",
        "NYSE":     "NYSE",
        "NYSEArca": "NYSE",
        "OTC Markets OTCPK": "OTC",
        "Other OTC": "OTC",
        "PNK":      "OTC",
        "Pink Sheets": "OTC",
        "YHD":      "HKG",
        "SES":      "SGP",
        "ASX":      "AUS"
    }
    return mapping.get(exchange, exchange) # Fallback to original if not in map

def fetch_batch(tickers: list[str], client, crumb: str) -> dict:
    """
    Fetch real-time quotes via Stealth API directly.
    """
    results = {}
    # Use EST (US/Eastern) for all internal timestamps to match user requirement
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("US/Eastern"))
    except Exception:
        from datetime import timedelta
        now = datetime.now(timezone.utc) - timedelta(hours=4)
    
    # Extract primary tickers
    primary_map = {clean_ticker(t): t for t in tickers}
    symbols = ','.join(primary_map.keys())
    
    all_symbols = list(primary_map.keys())
    symbols_str = ','.join(all_symbols)
    url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols_str}&crumb={crumb}'
    
    log.debug(f"Fetching {len(all_symbols)} tickers from Yahoo...")
    try:
        res = client.get(url, timeout=15)
        if res.status_code != 200:
            log.error(f"Failed to fetch batch. Status {res.status_code}: {res.text[:100]}")
            return results
            
        data = res.json()
        items = data.get('quoteResponse', {}).get('result', [])
        log.info(f"  Got {len(items)} responses from Yahoo for {len(all_symbols)} requested.")
        
        # Track missing tickers for logging
        found_symbols = {item.get('symbol') for item in items}
        missing = [s for s in all_symbols if s not in found_symbols]
        if missing:
            log.warning(f"  Missing from Yahoo: {', '.join(missing[:5])}{'...' if len(missing)>5 else ''}")

        for item in items:
            symbol = item.get('symbol')
            if not symbol or (symbol not in primary_map and symbol.upper() not in primary_map):
                continue

            original_ticker = primary_map.get(symbol) or primary_map.get(symbol.upper())
            
            # Triple-fallback for prices (Critical for ADRs/OTC)
            price      = item.get('regularMarketPrice')
            if price is None: price = item.get('postMarketPrice')
            if price is None: price = item.get('preMarketPrice')
            if price is None: price = item.get('previousClose')
            
            price_chg  = item.get('regularMarketChange') or item.get('postMarketChange') or 0
            change_pct = item.get('regularMarketChangePercent') or item.get('postMarketChangePercent') or 0
            volume     = item.get('regularMarketVolume') or 0
            avg_vol    = item.get('averageDailyVolume10Day') or 0
            exch_res   = item.get('fullExchangeName') or item.get('exchangeName') or item.get('exchange') or '???'
            market_st  = item.get('marketState')

            ext_price = None
            ext_pct = None
            ext_type = None
            if market_st in ('PRE', 'PREPRE'):
                ext_price = item.get('preMarketPrice')
                ext_pct   = item.get('preMarketChangePercent')
                ext_type  = 'PRE'
            elif market_st in ('POST', 'POSTPOST', 'CLOSED'):
                ext_price = item.get('postMarketPrice')
                ext_pct   = item.get('postMarketChangePercent')
                ext_type  = 'POST'

            vol_spike = None
            if volume and avg_vol and avg_vol > 0:
                vol_spike = round(volume / avg_vol, 2)

            entry = {
                'price':      round(price,      2) if price      is not None else None,
                'price_chg':  round(price_chg,  2) if price_chg  is not None else None,
                'change_pct': round(change_pct, 2) if change_pct is not None else None,
                'volume':     int(volume)           if volume               else None,
                'avg_volume': int(avg_vol)          if avg_vol              else None,
                'vol_spike':  vol_spike,
                'exchange':   exch_res,
                'updated':    now.strftime('%Y-%m-%d %H:%M EST'),
                'ext_price':  ext_price,
                'ext_pct':    ext_pct,
                'ext_type':   ext_type,
            }
            results[original_ticker] = entry

            if entry.get('price'):
                ext_str = f' [{ext_type} ${ext_price:.2f} {ext_pct:+.1f}%]' if ext_price is not None and ext_pct is not None else ''
                log.info(f'  {original_ticker:12s} ${entry["price"]:.2f} '
                         f'{entry.get("change_pct",0):+.1f}% '
                         f'[{entry.get("exchange")}] '
                         f'vol_spike={entry.get("vol_spike","N/A")}{ext_str}')
            else:
                log.warning(f'  {original_ticker:12s} no price data')
                
    except Exception as ex:
        log.error(f"Error fetching batch: {ex}")
        
    # Fill missing
    for t in tickers:
        if t not in results:
            log.warning(f'  {t:12s} no price data')
            results[t] = {}
            
    return results

def analyze_movers(prices: dict) -> dict:
    """
    Identify the most interesting movers from today's price data.
    Returns top gainers, top losers, and volume spikes.
    This powers the CPO PULSE strip in the terminal.
    """
    with_change = [(t, d) for t, d in prices.items()
                   if 'change_pct' in d and d['change_pct'] is not None
                   and t != '_meta']

    sorted_by_change = sorted(with_change, key=lambda x: x[1]['change_pct'], reverse=True)

    top_gainers = [{'ticker': t, 'change_pct': d['change_pct'], 'price': d.get('price')}
                   for t, d in sorted_by_change[:5] if d['change_pct'] > 0]

    top_losers  = [{'ticker': t, 'change_pct': d['change_pct'], 'price': d.get('price')}
                   for t, d in sorted_by_change[-5:] if d['change_pct'] < 0]

    # Volume spikes: vol_spike > 2x average = something is happening
    vol_spikes  = sorted(
        [{'ticker': t, 'vol_spike': d['vol_spike'], 'change_pct': d.get('change_pct')}
         for t, d in prices.items() if d.get('vol_spike', 0) and d.get('vol_spike', 0) >= 2.0
         and t != '_meta'],
        key=lambda x: x['vol_spike'], reverse=True
    )[:5]

    return {
        'top_gainers':  top_gainers,
        'top_losers':   [l | {'change_pct': l['change_pct']} for l in reversed(top_losers)],
        'volume_spikes': vol_spikes,
    }

async def async_run_fetch(tickers: list = None, dry_run: bool = False, skip_sync: bool = False) -> dict:
    if tickers is None:
        tickers = load_tickers()

    log.info(f'GIGACPO Live Price Fetcher — {len(tickers)} tickers')
    log.info(f'Output: {OUT_JS}')
    log.info('-' * 50)
    
    # Retrieve Valid/Cached Authenticated Session
    cookie_dict, crumb, user_agent = await get_valid_auth()
    
    client = requests.Session(impersonate='chrome146')
    client.headers.update({'User-Agent': user_agent})
    client.cookies.update(cookie_dict)

    all_prices = {}
    
    # Randomized Batching (8-13 tickers per burst)
    i = 0
    while i < len(tickers):
        batch_size = random.randint(8, 13)
        batch = tickers[i : i + batch_size]
        log.info(f'Batch [Size {len(batch)}]: {batch}')
        results = fetch_batch(batch, client, crumb)
        all_prices.update(results)
        
        i += len(batch)
        if i < len(tickers):
            delay = random.uniform(3.3, 10.0)
            log.info(f"Sleeping for {delay:.2f}s before next price batch...")
            await asyncio.sleep(delay)

    # Add metadata including top movers
    movers = analyze_movers(all_prices)
    
    # Use EST (US/Eastern) for display
    try:
        from zoneinfo import ZoneInfo
        now_est = datetime.now(ZoneInfo("US/Eastern"))
    except Exception:
        # Fallback if zoneinfo is weird on some Windows setups
        from datetime import timedelta
        now_est = datetime.now(timezone.utc) - timedelta(hours=4) # Rough EST
        
    refreshed_at_str = now_est.strftime("%Y-%m-%d %I:%M %p EST")
    # Compact format for UI: 2026-04-16 01:49 EST
    compact_ts = now_est.strftime("%Y-%m-%d %I:%M EST")
    
    all_prices['_meta'] = {
        'refreshed_at': refreshed_at_str,
        'refreshed_at_est': compact_ts,
        'refreshed_at_iso': now_est.isoformat(),
        'total_tickers': len(all_prices),
        'with_price': sum(1 for t, d in all_prices.items() if d.get('price') and t != '_meta'),
        **movers,
    }

    log.info('-' * 50)
    log.info(f'Fetched {all_prices["_meta"]["with_price"]}/{len(tickers)} prices')
    if movers['top_gainers']:
        log.info(f'Top gainer: {movers["top_gainers"][0]["ticker"]} +{movers["top_gainers"][0]["change_pct"]:.1f}%')
    if movers['top_losers']:
        log.info(f'Top loser:  {movers["top_losers"][0]["ticker"]} {movers["top_losers"][0]["change_pct"]:.1f}%')

    if not dry_run:
        # Write JSON (for audit/debugging)
        with open(OUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(all_prices, f, indent=2)
        log.info(f'Saved {OUT_JSON}')

        # Write JS (for HTML terminal consumption)
        with open(OUT_JS, 'w', encoding='utf-8') as f:
            f.write('// GIGACPO Live Prices — auto-generated by engine/live_prices.py\n')
            f.write('// DO NOT EDIT. Regenerate with: python engine/live_prices.py\n')
            f.write('window.LIVE_PRICES = ')
            json.dump(all_prices, f, separators=(',', ':'))
            f.write(';\n')
        log.info(f'Saved {OUT_JS}')

        # AUTO-SYNC to SFTP
        if not skip_sync:
            try:
                from remote_sync import RemoteSync
                rel_js = OUT_JS.relative_to(ROOT)
                RemoteSync.sync_file(OUT_JS)
            except Exception as e:
                log.error(f"Sync failed: {e}")
    else:
        log.info('[DRY RUN] Output not written')
        print(json.dumps(all_prices, indent=2)[:1000] + '\n...[truncated]')

    return all_prices

PRICE_TTL_SECONDS = 600

async def async_main():
    parser = argparse.ArgumentParser(description='GIGACPO Live Price Fetcher')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers')
    parser.add_argument('--dry-run', action='store_true', help='Print, do not write')
    parser.add_argument('--force', action='store_true', help='Override cache')
    parser.add_argument('--skip-sync', action='store_true', help='Do not upload to SFTP')
    args = parser.parse_args()

    if not args.force and not args.dry_run and OUT_JSON.exists():
        try:
            mtime = OUT_JSON.stat().st_mtime
            if (time.time() - mtime) < PRICE_TTL_SECONDS:
                log.info(f"Price cache fresh ({(time.time()-mtime)/60:.1f}m old). Skipping. Use --force to override.")
                return
        except: pass

    await async_run_fetch(tickers=args.tickers, dry_run=args.dry_run, skip_sync=args.skip_sync)

if __name__ == '__main__':
    asyncio.run(async_main())

