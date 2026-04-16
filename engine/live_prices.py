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
from stealth_navigator import StealthNavigator

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'database' / 'CPO_MASTER_DATA.json'
OUT_JS  = ROOT / 'database' / 'live_prices.js'
OUT_JSON = ROOT / 'database' / 'live_prices.json'

# Skip private/non-tradable tickers
SKIP_TICKERS = {'AYAR', 'RANV', 'CelestialAI', 'SCINTIL'}

BATCH_SIZE = 30
DELAY_BETWEEN_BATCHES = 1.0

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
            price      = item.get('regularMarketPrice')
            price_chg  = item.get('regularMarketChange')
            change_pct = item.get('regularMarketChangePercent')
            volume     = item.get('regularMarketVolume')
            avg_vol    = item.get('averageDailyVolume10Day')
            exch_res   = item.get('fullExchangeName') or item.get('exchangeName') or item.get('exchange') or item.get('exchangeDataDelayedBy','??')

            vol_spike = None
            if volume and avg_vol and avg_vol > 0:
                vol_spike = round(volume / avg_vol, 2)

            # Extended-hours price (AH or PM)
            post_price = item.get('postMarketPrice')
            post_pct   = item.get('postMarketChangePercent')
            pre_price  = item.get('preMarketPrice')
            pre_pct    = item.get('preMarketChangePercent')

            ext_price, ext_pct, ext_type = None, None, None
            if post_price is not None:
                ext_price, ext_pct, ext_type = post_price, post_pct, 'AH'
            elif pre_price is not None:
                ext_price, ext_pct, ext_type = pre_price, pre_pct, 'PM'

            entry = {
                'price':      round(price,      2) if price      is not None else None,
                'price_chg':  round(price_chg,  2) if price_chg  is not None else None,
                'change_pct': round(change_pct, 2) if change_pct is not None else None,
                'volume':     int(volume)           if volume               else None,
                'avg_volume': int(avg_vol)          if avg_vol              else None,
                'vol_spike':  vol_spike,
                'ext_price':  round(ext_price, 2)  if ext_price is not None else None,
                'ext_pct':    round(ext_pct,   2)  if ext_pct   is not None else None,
                'ext_type':   ext_type,
                'exchange':   exch_res,
                'updated':    now.strftime('%Y-%m-%d %H:%M EST'),
            }
            entry = {k: v for k, v in entry.items() if v is not None}
            results[original_ticker] = entry

            if entry.get('price'):
                ext_str = f' [{ext_type} ${ext_price:.2f} {ext_pct:+.1f}%]' if ext_price else ''
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

async def async_run_fetch(tickers: list = None, dry_run: bool = False) -> dict:
    if tickers is None:
        tickers = load_tickers()

    log.info(f'GIGACPO Live Price Fetcher — {len(tickers)} tickers')
    log.info(f'Output: {OUT_JS}')
    log.info('-' * 50)
    
    # Setup Stealth Session
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    cookies_list, crumb = await nav.get_session_state('https://finance.yahoo.com/quote/AAPL')
    await nav.close()
    
    cookie_dict = {c['name']: c['value'] for c in cookies_list}
    client = requests.Session(impersonate='chrome')
    client.headers.update({'User-Agent': nav.current_ua})
    client.cookies.update(cookie_dict)

    all_prices = {}
    batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]

    for i, batch in enumerate(batches):
        log.info(f'Batch {i+1}/{len(batches)}: {batch}')
        results = fetch_batch(batch, client, crumb)
        all_prices.update(results)
        if i < len(batches) - 1:
            time.sleep(DELAY_BETWEEN_BATCHES)

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
    else:
        log.info('[DRY RUN] Output not written')
        print(json.dumps(all_prices, indent=2)[:1000] + '\n...[truncated]')

    return all_prices

def run_fetch(tickers: list = None, dry_run: bool = False) -> dict:
    return asyncio.run(async_run_fetch(tickers, dry_run))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GIGACPO Live Price Fetcher')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers (default: all public)')
    parser.add_argument('--dry-run', action='store_true', help='Print output, do not write files')
    args = parser.parse_args()
    run_fetch(tickers=args.tickers, dry_run=args.dry_run)
