import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../engine')))
"""
engine/openbb_fetcher.py
========================
OpenBB v4 supplemental data fetcher for GIGACPO terminal.

PURPOSE: Adds analyst estimates + institutional ownership + short interest to the master dataset.
         This is ADDITIVE ONLY — never overwrites existing yfinance financials data.
         Writes to human_research.openbb_supplement{} on each ticker.

FIELDS ADDED:
    analyst_target_mean   - Consensus mean price target across all analysts
    analyst_target_high   - Most bullish analyst target
    analyst_target_low    - Most bearish analyst target
    analyst_count         - Number of analysts covering the stock
    analyst_buy_pct       - % of analysts with Buy/Strong Buy rating
    inst_ownership_pct    - Institutional ownership as % of float
    short_interest_pct    - Short interest as % of float (contrarian signal)
    last_updated          - ISO timestamp of last successful update

WHY THESE FIELDS MATTER FOR CPO INVESTING:
    - analyst_count < 5 = undercovered (hiddenness signal)
    - inst_ownership_pct < 20% = institutional accumulation not yet underway
    - short_interest_pct > 15% = high short interest = potential short squeeze on catalyst
    - analyst_buy_pct > 80% = wall street consensus (reducing hidden alpha value)
"""

import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf  # Primary source — already installed, zero new deps

# Optional: Try OpenBB for provider-agnostic access
try:
    from openbb import obb
    OPENBB_AVAILABLE = True
except ImportError:
    OPENBB_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'database' / 'AI_MASTER_DATA.json'
JS_PATH = ROOT / 'database' / 'dashboard_data.js'

# Tickers to skip for analyst data (private companies, ETFs with no analyst coverage)
SKIP_TICKERS = {'AYAR', 'RANV', 'CelestialAI', 'SCINTIL', 'PTF', 'LADR', 'XSD'}

# Exported for tests
BUCKET_MULT_PRIVATE = 'Private'

def momentumScore_equivalent(perf1y):
    """Mirror of the JS momentumScore() function — exported for test validation."""
    if perf1y is None: return 4
    if perf1y > 300: return 5
    if perf1y > 100: return 9
    if perf1y > 40:  return 10
    if perf1y > 10:  return 7
    if perf1y > 0:   return 5
    if perf1y > -25: return 3
    return 1

# Rate limiting: be respectful to free APIs
DELAY_BETWEEN_REQUESTS = 0.0  # seconds


def clean_ticker(ticker: str) -> str:
    """Extract primary ticker from compound 'A.XX / B' format."""
    return ticker.split(' / ')[0].strip()


def _get_yf_supplement(ticker_symbol: str, entry: dict) -> dict:
    """
    Primary: Use stealth-fetched financials from CPO_MASTER_DATA.json
    - targetMeanPrice, targetHighPrice, targetLowPrice
    - numberOfAnalystOpinions
    - recommendationMean (1=Strong Buy ... 5=Strong Sell)
    - heldPercentInstitutions
    - shortPercentOfFloat
    """
    result = {}
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
        rec_mean    = get_raw(fin_data, 'recommendationMean')  # 1.0=Strong Buy, 3.0=Hold, 5.0=Strong Sell
        inst_pct    = get_raw(stats, 'heldPercentInstitutions')
        short_pct   = get_raw(stats, 'shortPercentOfFloat')
        current_price = get_raw(fin_data, 'currentPrice') or get_raw(summary, 'regularMarketPrice')

        # Convert recommendation mean to buy% estimate
        # 1.0-1.5 = Strong Buy, 1.5-2.5 = Buy, 2.5-3.5 = Hold, 3.5+ = Sell
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

        log.info(f'  {ticker_symbol}: analysts={n_analysts}, target=${target_mean}, inst={inst_pct}')

    except Exception as ex:
        log.warning(f'  {ticker_symbol}: JSON extraction error — {ex}')

    return result


def _get_openbb_supplement(ticker_symbol: str) -> dict:
    """
    Secondary: Use OpenBB for additional data where raw yfinance JSON fails.
    Prioritizes 'tmx' provider for estimates as it is often more stable than yfinance.
    """
    if not OPENBB_AVAILABLE:
        return {}
    result = {}
    try:
        # 1. Try TMX for Consensus (Usually returns buy/sell/hold counts)
        est = obb.equity.estimates.consensus(symbol=ticker_symbol, provider='tmx')
        if est and hasattr(est, 'results') and est.results:
            r = est.results[0]
            if getattr(r, 'target_consensus', None): result['analyst_target_mean'] = r.target_consensus
            if getattr(r, 'total_analysts', None):   result['analyst_count'] = r.total_analysts
            if getattr(r, 'buy_ratings', None):     result['analyst_buy_count'] = r.buy_ratings
            if getattr(r, 'sell_ratings', None):    result['analyst_sell_count'] = r.sell_ratings
            
            # Derived Buy %
            if r.buy_ratings is not None and r.total_analysts:
                result['analyst_buy_pct'] = round((r.buy_ratings / r.total_analysts) * 100, 1)

        # 2. Try for Institutional / Short Interest (Often redundant but good fallback)
        # obb.equity.ownership.institutional (often requires FMP/Intrinio key)
    except Exception as ex:
        log.debug(f'  {ticker_symbol}: openbb supplement skipped — {ex}')

    return result


def fetch_supplement(ticker_symbol: str, bucket: str, entry: dict = None) -> dict:
    """Combine yfinance + OpenBB supplement data."""
    if ticker_symbol in SKIP_TICKERS or bucket == 'Private':
        return {}

    # Clean compound tickers: 'SIVE.ST / SIVEF' -> 'SIVE.ST'
    yf_ticker = clean_ticker(ticker_symbol)

    result = _get_yf_supplement(yf_ticker, entry)
    obb_result = _get_openbb_supplement(yf_ticker)
    result.update(obb_result)  # OpenBB supplements, doesn't replace

    if result:
        result['last_updated'] = datetime.now(timezone.utc).isoformat()

    return result


def run_fetch(tickers: list = None, force: bool = False, dry_run: bool = False):
    """
    Main entry point. Fetches supplement data for all (or specified) tickers.

    Args:
        tickers: list of ticker symbols. If None, fetches all non-private.
        force: if True, re-fetches even if data exists.
        dry_run: if True, prints what would be fetched but doesn't save.
    """
    with open(DB_PATH, encoding='utf-8') as f:
        data = json.load(f)

    if tickers is None:
        tickers = [t for t, e in data.items()
                   if e.get('human_research', {}).get('Bucket') != 'Private'
                   and t not in SKIP_TICKERS]

    log.info(f'OpenBB Supplement Fetcher — {len(tickers)} tickers to process')
    log.info(f'OpenBB available: {OPENBB_AVAILABLE}')
    log.info(f'Dry run: {dry_run}')
    log.info('-' * 50)

    updated = 0
    skipped = 0
    errors = 0

    for i, ticker in enumerate(tickers):
        if ticker not in data:
            log.warning(f'[{i+1}/{len(tickers)}] {ticker}: NOT IN DATABASE — skipping')
            skipped += 1
            continue

        entry = data[ticker]
        h = entry.get('human_research', {})
        bucket = h.get('Bucket', '')

        # Check if already fetched and not forcing
        existing = h.get('openbb_supplement', {})
        if existing and not force:
            log.info(f'[{i+1}/{len(tickers)}] {ticker}: already has supplement data (last: {existing.get("last_updated","?")}), skipping')
            skipped += 1
            continue

        log.info(f'[{i+1}/{len(tickers)}] Fetching {ticker} ({bucket})...')

        supplement = fetch_supplement(ticker, bucket, entry)

        if supplement:
            if not dry_run:
                data[ticker]['human_research']['openbb_supplement'] = supplement
            updated += 1
            log.info(f'  -> Got {len(supplement)} fields: {list(supplement.keys())}')
        else:
            log.info(f'  -> No data returned')
            skipped += 1

        # Rate limiting
        if i < len(tickers) - 1:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    log.info('-' * 50)
    log.info(f'Complete: {updated} updated, {skipped} skipped, {errors} errors')

    if not dry_run and updated > 0:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        log.info(f'Saved to {DB_PATH}')

        # Sync JS
        with open(JS_PATH, 'w', encoding='utf-8') as f:
            f.write('window.CPO_MASTER_DATA = ')
            json.dump(data, f, indent=2)
            f.write(';')
        log.info(f'Synced {JS_PATH}')

    return {'updated': updated, 'skipped': skipped, 'errors': errors}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='GIGACPO OpenBB Supplement Fetcher')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers to fetch (default: all)')
    parser.add_argument('--force', action='store_true', help='Re-fetch even if data exists')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fetched without saving')
    args = parser.parse_args()
    run_fetch(tickers=args.tickers, force=args.force, dry_run=args.dry_run)
