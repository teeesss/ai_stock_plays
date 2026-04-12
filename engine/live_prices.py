"""
engine/live_prices.py
======================
Real-time price fetcher for the GIGACPO terminal.

Uses yfinance directly (OpenBB v4.7.1 has a known broken import on this machine:
`cannot import name 'OBBject_EquityInfo'` — openbb-equity extension mismatch with openbb-core).
Tracked in TASKS.md. Will switch to OpenBB when they fix the extension schema.

WHY yfinance IS FINE HERE:
- yfinance already gets data from Yahoo Finance in real-time (15-min delayed for free)
- OpenBB's price.quote endpoint uses yfinance as its underlying provider anyway
- yf.download() handles batch fetching efficiently
- Covers all our global symbols: US, OTC, .T, .TW, .DE, .PA, .KL, etc.

OUTPUT: database/live_prices.js
  window.LIVE_PRICES = {
    "CRDO":    { price: 28.5, change_pct: 2.3, volume: 1234567, updated: "2026-04-12T..." },
    "BESIY":   { price: 12.1, change_pct: -0.8, volume: 45678,  updated: "..." },
    "LPK.DE":  { price: 9.8,  change_pct: 1.1, volume: 23456,   updated: "..." },
    ...
    "_meta":   { refreshed_at: "2026-04-12T17:30:00Z", total_tickers: 113,
                 top_gainers: [...], top_losers: [...], volume_spikes: [...] }
  };

RUN:
    python engine/live_prices.py              # Fetch all tickers
    python engine/live_prices.py --tickers CRDO BESIY ASMVY   # Specific tickers
    python engine/live_prices.py --dry-run    # Print output, don't write files
"""

import json
import time
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'database' / 'CPO_MASTER_DATA.json'
OUT_JS  = ROOT / 'database' / 'live_prices.js'
OUT_JSON = ROOT / 'database' / 'live_prices.json'

# Skip private/non-tradable tickers
SKIP_TICKERS = {'AYAR', 'RANV', 'CelestialAI', 'SCINTIL'}

# Batch size for yf.download() — 20 is safe without hitting rate limits
BATCH_SIZE = 20
DELAY_BETWEEN_BATCHES = 1.0


def load_tickers() -> list[str]:
    """Load all public (non-private) tickers from the master database."""
    with open(DB_PATH, encoding='utf-8') as f:
        data = json.load(f)
    return [t for t, e in data.items()
            if e.get('human_research', {}).get('Bucket') != 'Private'
            and t not in SKIP_TICKERS]


def fetch_batch(tickers: list[str]) -> dict:
    """
    Fetch real-time quotes for a batch of tickers via yfinance.
    Strategy:
      1. Try fast_info (fast, works for US/OTC/Europe)
      2. On 401/None: Try yf.download() for the last 2 days (better crumb handling)
      3. Mark as no-data if still fails
    """
    results = {}
    now = datetime.now(timezone.utc).isoformat()

    for ticker in tickers:
        entry = _fetch_single(ticker, now)
        results[ticker] = entry
        if entry.get('price'):
            log.info(f'  {ticker:12s} ${entry["price"]:.2f} '
                     f'{entry.get("change_pct",0):+.1f}% '
                     f'vol_spike={entry.get("vol_spike","N/A")}')
        else:
            log.warning(f'  {ticker:12s} no price data')

    return results



def clean_ticker(ticker: str) -> str:
    """Extract primary ticker from compound 'A.XX / B' format."""
    return ticker.split(' / ')[0].strip()


def _fetch_single(ticker: str, now: str) -> dict:
    """Fetch a single ticker — try fast_info, fall back to yf.download()."""
    entry = {}
    primary = clean_ticker(ticker)
    try:
        t = yf.Ticker(primary)
        info = t.fast_info
        price = getattr(info, 'last_price', None)
        prev_close = getattr(info, 'previous_close', None)
        volume    = getattr(info, 'last_volume', None)
        avg_vol   = getattr(info, 'three_month_average_volume', None)

        # fast_info 401 fallback: use yf.download() for last 2 trading days
        if price is None:
            hist = yf.download(primary, period='2d', interval='1d', progress=False, auto_adjust=True)
            if hist is not None and len(hist) >= 2:
                price     = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Close'].iloc[-2])
                volume    = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else None
                avg_vol   = None

        change_pct = None
        if price and prev_close and prev_close > 0:
            change_pct = round(((price / prev_close) - 1) * 100, 2)

        vol_spike = None
        if volume and avg_vol and avg_vol > 0:
            vol_spike = round(volume / avg_vol, 2)

        entry = {'price': round(price, 2) if price else None, 'change_pct': change_pct,
                 'volume': int(volume) if volume else None, 'avg_volume': int(avg_vol) if avg_vol else None,
                 'vol_spike': vol_spike, 'updated': now}
        entry = {k: v for k, v in entry.items() if v is not None}

    except Exception as ex:
        log.warning(f'  {ticker}: error — {type(ex).__name__}: {ex}')

    return entry


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


def run_fetch(tickers: list = None, dry_run: bool = False) -> dict:
    """
    Main entry point. Fetches live prices and writes live_prices.js + live_prices.json.
    """
    if tickers is None:
        tickers = load_tickers()

    log.info(f'GIGACPO Live Price Fetcher — {len(tickers)} tickers')
    log.info(f'Output: {OUT_JS}')
    log.info('-' * 50)

    all_prices = {}
    batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]

    for i, batch in enumerate(batches):
        log.info(f'Batch {i+1}/{len(batches)}: {batch}')
        results = fetch_batch(batch)
        all_prices.update(results)
        if i < len(batches) - 1:
            time.sleep(DELAY_BETWEEN_BATCHES)

    # Add metadata including top movers
    movers = analyze_movers(all_prices)
    now = datetime.now(timezone.utc).isoformat()
    all_prices['_meta'] = {
        'refreshed_at': now,
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GIGACPO Live Price Fetcher')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers (default: all public)')
    parser.add_argument('--dry-run', action='store_true', help='Print output, do not write files')
    args = parser.parse_args()
    run_fetch(tickers=args.tickers, dry_run=args.dry_run)
