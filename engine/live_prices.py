"""
engine/live_prices.py [V28]
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

import argparse
import asyncio
import json
import logging
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# V28: Setup Logging BEFORE any local imports that might hijack root
ROOT = Path(__file__).parent.parent
OUT_JS = ROOT / "database" / "live_prices.js"
OUT_JSON = ROOT / "database" / "live_prices.json"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# ── LOCAL IMPORTS (Must be after logging setup) ──────────────────────
try:
    from error_monitor import init_error_monitor
except ImportError:
    from engine.error_monitor import init_error_monitor
init_error_monitor()

from curl_cffi import requests

try:
    from yahoo_auth import get_valid_auth
except ImportError:
    from engine.yahoo_auth import get_valid_auth

try:
    from ticker_utils import load_master_tickers
except ImportError:
    from engine.ticker_utils import load_master_tickers
try:
    from market_session import MarketSession
except ImportError:
    from engine.market_session import MarketSession

BATCH_SIZE = 25


def load_tickers() -> list[str]:
    """Load only the static terminal tickers (Root + AI)."""
    return load_master_tickers("static")


def clean_ticker(ticker: str) -> str:
    """Extract primary ticker from compound 'A.XX / B' format."""
    return ticker.split(" / ")[0].strip()


def calculate_session_data(item: dict, tm: int) -> tuple:
    """
    V28: Greedy Session Extraction Logic
    Exhaustively searches for AH/PRE/OVN prices based on time, even if primary fields are missing.
    """
    price = item.get("regularMarketPrice")
    bid = item.get("bid")
    ask = item.get("ask")
    m_state = item.get("marketState", "REGULAR")

    # Standard Fields
    a_p, a_pct = item.get("postMarketPrice"), item.get("postMarketChangePercent")
    p_p, p_pct = item.get("preMarketPrice"), item.get("preMarketChangePercent")
    o_p, o_pct = (
        item.get("overnightMarketPrice"),
        item.get("overnightMarketChangePercent"),
    )

    ext_price, ext_pct, ext_type = None, None, "REG"

    # Session Priority Logic
    if 400 <= tm < 930:  # PRE-MARKET (4:00 AM - 9:30 AM)
        if p_p is not None:
            ext_price, ext_pct, ext_type = p_p, p_pct, "PRE"
        elif o_p is not None:
            ext_price, ext_pct, ext_type = o_p, o_pct, "OVN"
        elif a_p is not None and tm < 700:  # Early morning AH residue
            ext_price, ext_pct, ext_type = a_p, a_pct, "AH"

    elif 1600 <= tm < 2000:  # AFTER-HOURS (4:00 PM - 8:00 PM)
        if a_p is not None:
            ext_price, ext_pct, ext_type = a_p, a_pct, "AH"
        elif o_p is not None:
            ext_price, ext_pct, ext_type = o_p, o_pct, "OVN"
        elif p_p is not None and tm < 1630:  # Stale PRE residue? Only if close
            ext_price, ext_pct, ext_type = p_p, p_pct, "PRE"

    elif tm >= 2000 or tm < 400:  # OVERNIGHT (8:00 PM - 4:00 AM)
        if o_p is not None:
            ext_price, ext_pct, ext_type = o_p, o_pct, "OVN"
        elif a_p is not None:
            ext_price, ext_pct, ext_type = a_p, a_pct, "AH"
        elif p_p is not None:
            ext_price, ext_pct, ext_type = p_p, p_pct, "PRE"

    # Midpoint Fallback for ALL extended sessions if Price is missing but Bid/Ask exist
    if ext_price is None and bid and ask and not (930 <= tm < 1600):
        # Only use midpoint if it differs from regular price (implies active session)
        mid = (bid + ask) / 2
        if price and abs(mid - price) / price > 0.0005:
            ext_price = mid
            ext_pct = ((ext_price / price) - 1) * 100 if price else 0
            # Label based on time
            if 400 <= tm < 930:
                ext_type = "PRE"
            elif 1600 <= tm < 2000:
                ext_type = "AH"
            else:
                ext_type = "OVN"

    # Percent calculation fallback
    if ext_price is not None and ext_pct is None and price:
        ext_pct = ((ext_price / price) - 1) * 100

    # V23.87 Guard: Force LIVE if in regular hours
    if m_state.startswith("REGULAR") and (930 <= tm < 1600):
        ext_type = "LIVE"

    return ext_price, ext_pct, ext_type


def get_exchange_abbr(exchange: str) -> str:
    """Standardizes exchange names into clean abbreviations."""
    if not exchange:
        return "???"

    mapping = {
        "NasdaqGS": "NASDAQ",
        "NasdaqGM": "NASDAQ",
        "NasdaqCM": "NASDAQ",
        "Nasdaq": "NASDAQ",
        "NMS": "NASDAQ",
        "National Market System": "NASDAQ",
        "New York Stock Exchange": "NYSE",
        "NYSE": "NYSE",
        "NYSEArca": "NYSE",
        "OTC Markets OTCPK": "OTC",
        "Other OTC": "OTC",
        "PNK": "OTC",
        "Pink Sheets": "OTC",
        "YHD": "HKG",
        "SES": "SGP",
        "ASX": "AUS",
    }
    return mapping.get(exchange, exchange)  # Fallback to original if not in map


def fetch_batch(tickers: list[str], client, crumb: str) -> dict:
    """
    Fetch real-time quotes via Stealth API directly.
    """
    results = {}
    # Use EST (US/Eastern) for all internal timestamps anchored to UTC
    now_utc = datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo

        now = now_utc.astimezone(ZoneInfo("US/Eastern"))
    except Exception:
        now = now_utc - timedelta(hours=4)

    try:
        from ticker_utils import resolve_ticker
    except ImportError:
        from engine.ticker_utils import resolve_ticker

    # Extract primary tickers
    # V28.3: Resolve aliases (SHINKO -> 6967.T) before batching
    primary_map = {resolve_ticker(clean_ticker(t)): t for t in tickers}
    symbols = ",".join(primary_map.keys())

    all_symbols = list(primary_map.keys())
    symbols_str = ",".join(all_symbols)
    # V22.94: Request explicit fields including Overnight (BOATS) data
    # V28.8: Added marketCap, trailingPE, totalRevenue for dashboard enrichment
    fields = "regularMarketPrice,regularMarketChange,regularMarketChangePercent,regularMarketVolume,averageDailyVolume10Day,marketState,postMarketPrice,postMarketChange,postMarketChangePercent,preMarketPrice,preMarketChange,preMarketChangePercent,overnightMarketPrice,overnightMarketChange,overnightMarketChangePercent,bid,ask,fullExchangeName,exchangeName,exchange,marketCap,trailingPE,totalRevenue,regularMarketPreviousClose"
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols_str}&fields={fields}&overnightPrice=true&crumb={crumb}"

    log.debug(f"Fetching {len(all_symbols)} tickers from Yahoo...")
    try:
        res = client.get(url, timeout=15)
        if res.status_code != 200:
            log.error(f"Failed to fetch batch. Status {res.status_code}: {res.text[:100]}")
            return results

        data = res.json()
        items = data.get("quoteResponse", {}).get("result", [])
        log.info(f"  Got {len(items)} responses from Yahoo for {len(all_symbols)} requested.")

        # Track missing tickers for logging
        found_symbols = {item.get("symbol") for item in items}
        missing = [s for s in all_symbols if s not in found_symbols]
        if missing:
            log.warning(
                f"  Missing from Yahoo: {', '.join(missing[:5])}{'...' if len(missing)>5 else ''}"
            )

        for item in items:
            symbol = item.get("symbol")
            if not symbol or (symbol not in primary_map and symbol.upper() not in primary_map):
                continue

            original_ticker = primary_map.get(symbol) or primary_map.get(symbol.upper())

            tm = now.hour * 100 + now.minute
            exch_res = (
                item.get("fullExchangeName")
                or item.get("exchangeName")
                or item.get("exchange")
                or "???"
            )
            m_state = item.get("marketState", "REGULAR")

            # Triple-fallback for prices (Critical for ADRs/OTC)
            price = item.get("regularMarketPrice")
            if price is None:
                price = item.get("postMarketPrice")
            if price is None:
                price = item.get("preMarketPrice")
            if price is None:
                price = item.get("previousClose")

            price_chg = (
                item.get("regularMarketChange")
                if item.get("regularMarketChange") is not None
                else (
                    item.get("postMarketChange") if item.get("postMarketChange") is not None else 0
                )
            )
            change_pct = item.get("regularMarketChangePercent") or 0
            volume = (
                item.get("regularMarketVolume")
                if item.get("regularMarketVolume") is not None
                else 0
            )
            avg_vol = (
                item.get("averageDailyVolume10Day")
                if item.get("averageDailyVolume10Day") is not None
                else 0
            )
            bid = item.get("bid")
            ask = item.get("ask")

            # V23.90: Centralized Session Extraction
            ext_price, ext_pct, ext_type = calculate_session_data(item, tm)

            vol_spike = round(volume / avg_vol, 2) if avg_vol and avg_vol > 0 else 0

            # V30.6.10: Authoritative Anchor Logic
            # During PRE/AH, regularMarketPrice IS the last close.
            close_price = item.get("regularMarketPrice") or item.get("previousClose")

            # prev_close must be the session BEFORE the last close
            prev_close = item.get("regularMarketPreviousClose") or item.get("previousClose")
            # Emergency fallback: if prev_close is same as close, try to calculate it
            if prev_close == close_price and item.get("regularMarketChange") is not None:
                prev_close = close_price - item.get("regularMarketChange")

            entry = {
                "price": round(price, 2) if price is not None else None,
                "close_price": (round(close_price, 2) if close_price is not None else None),
                "prev_close": (round(prev_close, 2) if prev_close is not None else None),
                "price_chg": round(price_chg, 2) if price_chg is not None else None,
                "change_pct": round(change_pct, 2) if change_pct is not None else None,
                "volume": int(volume) if volume else None,
                "avg_volume": int(avg_vol) if avg_vol else None,
                "vol_spike": vol_spike,
                "exchange": exch_res,
                "updated": now.strftime("%Y-%m-%d %H:%M EST"),
                "timestamp": time.time(),
                "ext_price": round(ext_price, 2) if ext_price is not None else None,
                "ext_pct": round(ext_pct, 2) if ext_pct is not None else None,
                "ext_type": ext_type,
                "market_cap": item.get("marketCap"),
                "pe": item.get("trailingPE"),
                "rev": item.get("totalRevenue"),
            }
            results[original_ticker] = entry

            if entry.get("price"):
                ext_str = (
                    f" [{ext_type} ${ext_price:.2f} {ext_pct:+.1f}%]"
                    if ext_price is not None and ext_pct is not None
                    else ""
                )
                log.info(
                    f'  {original_ticker:12s} ${entry["price"]:.2f} '
                    f'{entry.get("change_pct",0):+.1f}% '
                    f'[{entry.get("exchange")}] '
                    f'vol_spike={entry.get("vol_spike","N/A")}{ext_str}'
                )
            else:
                log.warning(f"  {original_ticker:12s} no price data")

    except Exception as ex:
        log.error(f"Error fetching batch: {ex}")

    # V26.9: Retry Logic for Taiwan tickers (.TW -> .TWO)
    # If a ticker ending in .TW failed, try .TWO (Taipei Exchange)
    found_symbols = {item.get("symbol").upper() for item in items}
    missing_tw = [
        s for s in all_symbols if s.upper().endswith(".TW") and s.upper() not in found_symbols
    ]

    if missing_tw:
        retry_map = {s.upper().replace(".TW", ".TWO"): s for s in missing_tw}
        retry_symbols = ",".join(retry_map.keys())
        log.info(f"  Retrying {len(retry_map)} Taiwan tickers with .TWO suffix: {retry_symbols}")

        try:
            url_retry = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={retry_symbols}&fields={fields}&overnightPrice=true&crumb={crumb}"
            res_retry = client.get(url_retry, timeout=10)
            if res_retry.status_code == 200:
                data_retry = res_retry.json()
                items_retry = data_retry.get("quoteResponse", {}).get("result", [])
                log.info(f"  Got {len(items_retry)} retry responses.")

                for item in items_retry:
                    symbol = item.get("symbol").upper()
                    original_ticker = retry_map.get(symbol)
                    if not original_ticker:
                        continue

                    tm = now.hour * 100 + now.minute
                    exch_res = (
                        item.get("fullExchangeName")
                        or item.get("exchangeName")
                        or item.get("exchange")
                        or "???"
                    )

                    price = item.get("regularMarketPrice")
                    if price is None:
                        price = item.get("postMarketPrice")
                    if price is None:
                        price = item.get("preMarketPrice")
                    if price is None:
                        price = item.get("previousClose")

                    price_chg = item.get("regularMarketChange") or 0
                    change_pct = item.get("regularMarketChangePercent") or 0
                    volume = item.get("regularMarketVolume") or 0
                    avg_vol = item.get("averageDailyVolume10Day") or 0

                    ext_price, ext_pct, ext_type = calculate_session_data(item, tm)
                    vol_spike = round(volume / avg_vol, 2) if avg_vol and avg_vol > 0 else 0

                    close_price = item.get("regularMarketPrice") or item.get("previousClose")
                    prev_close = item.get("regularMarketPreviousClose") or item.get("previousClose")

                    entry = {
                        "price": round(price, 2) if price is not None else None,
                        "close_price": (round(close_price, 2) if close_price is not None else None),
                        "price_chg": (round(price_chg, 2) if price_chg is not None else None),
                        "change_pct": (round(change_pct, 2) if change_pct is not None else None),
                        "volume": int(volume) if volume else None,
                        "avg_volume": int(avg_vol) if avg_vol else None,
                        "vol_spike": vol_spike,
                        "exchange": exch_res,
                        "updated": now.strftime("%Y-%m-%d %H:%M EST"),
                        "timestamp": time.time(),
                        "ext_price": ext_price,
                        "ext_pct": ext_pct,
                        "ext_type": ext_type,
                        "prev_close": prev_close,
                        "market_cap": item.get("marketCap"),
                        "pe": item.get("trailingPE"),
                        "rev": item.get("totalRevenue"),
                    }
                    results[original_ticker] = entry
                    log.info(f'  {original_ticker:12s} ${entry["price"]:.2f} (via {symbol})')
        except Exception as ex_retry:
            log.error(f"Error in Taiwan retry: {ex_retry}")

    # Fill missing
    for t in tickers:
        if t not in results:
            log.warning(f"  {t:12s} no price data")
            results[t] = {}

    return results


def analyze_movers(prices: dict) -> dict:
    """
    Identify the most interesting movers from today's price data.
    Returns top gainers, top losers, and volume spikes.
    This powers the CPO PULSE strip in the terminal.
    """
    # V24.6: Data Hygiene - Only consider movers updated in the last 6 hours
    now_ts = time.time()
    fresh_prices = {
        t: d for t, d in prices.items() if t != "_meta" and (now_ts - d.get("timestamp", 0)) < 21600
    }

    with_change = [
        (t, d) for t, d in fresh_prices.items() if "change_pct" in d and d["change_pct"] is not None
    ]

    sorted_by_change = sorted(with_change, key=lambda x: x[1]["change_pct"], reverse=True)

    top_gainers = [
        {"ticker": t, "change_pct": d["change_pct"], "price": d.get("price")}
        for t, d in sorted_by_change[:5]
        if d["change_pct"] > 0
    ]

    top_losers = [
        {"ticker": t, "change_pct": d["change_pct"], "price": d.get("price")}
        for t, d in sorted_by_change[-5:]
        if d["change_pct"] < 0
    ]

    # Volume spikes: vol_spike > 2x average = something is happening
    vol_spikes = sorted(
        [
            {
                "ticker": t,
                "vol_spike": d["vol_spike"],
                "change_pct": d.get("change_pct"),
            }
            for t, d in fresh_prices.items()
            if d.get("vol_spike", 0) and d.get("vol_spike", 0) >= 2.0
        ],
        key=lambda x: x["vol_spike"],
        reverse=True,
    )[:5]

    return {
        "top_gainers": top_gainers,
        "top_losers": [item | {"change_pct": item["change_pct"]} for item in reversed(top_losers)],
        "volume_spikes": vol_spikes,
    }


async def async_run_fetch(
    tickers: list = None,
    force: bool = False,
    dry_run: bool = False,
    skip_sync: bool = False,
) -> dict:
    if tickers is None:
        tickers = load_tickers()

    # V26.14: Hierarchy-Driven Weekend Stasis Gate
    session = MarketSession()
    if not force and session.is_market_stasis():
        log.info("[STASIS] Market is currently closed (Weekend). Skipping fetch to preserve cache.")
        # Load existing for the return, but don't fetch anything new
        if OUT_JSON.exists():
            try:
                with open(OUT_JSON, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    # Load existing prices for TTL check
    existing_all = {}
    if OUT_JSON.exists():
        try:
            with open(OUT_JSON, "r", encoding="utf-8") as f:
                existing_all = json.load(f)
        except:
            pass

    # V26.9: Granular 15-Minute Lock (Per-Ticker TTL) with improved logging
    if not force:
        now_ts = time.time()
        stale = []
        min_remaining = 999999

        for t in tickers:
            # V26.9: Clean ticker before cache check to ensure match (4062.T / IBIDY -> 4062.T)
            clean_t = clean_ticker(t)
            ts = existing_all.get(t, {}).get("timestamp") or existing_all.get(clean_t, {}).get(
                "timestamp", 0
            )

            diff = now_ts - ts
            if diff >= 900:  # 15 minutes
                stale.append(t)
            else:
                rem = 900 - diff
                if rem < min_remaining:
                    min_remaining = rem

        skipped = len(tickers) - len(stale)
        if skipped > 0:
            m, s = divmod(int(min_remaining), 60)
            log.info(f"[CACHE] {skipped} tickers are within 15m TTL. Next refresh in {m}m {s}s.")
            log.info(f"[CACHE] Only fetching {len(stale)} stale assets.")
            if not stale:
                log.info("All requested tickers are fresh. Run aborted.")
                return existing_all
        tickers = stale

    log.info(f"GIGACPO Live Price Fetcher - {len(tickers)} tickers to refresh")
    log.info(f"Output: {OUT_JS}")
    log.info("-" * 50)

    # Retrieve Valid/Cached Authenticated Session
    cookie_dict, crumb, user_agent = await get_valid_auth()

    client = requests.Session(impersonate="chrome146")
    client.headers.update({"User-Agent": user_agent})
    client.cookies.update(cookie_dict)

    all_prices = existing_all.copy()

    # Randomized Batching (8-13 tickers per burst)
    i = 0
    while i < len(tickers):
        batch_size = random.randint(8, 13)
        batch = tickers[i : i + batch_size]
        log.info(f"Batch [Size {len(batch)}]: {batch}")
        results = fetch_batch(batch, client, crumb)
        all_prices.update(results)

        i += len(batch)
        if i < len(tickers):
            # V25.2: Relaxed delay to 2.0-6.0s to improve stealth and avoid Yahoo rate limits
            delay = random.uniform(2.0, 6.0)
            log.info(f"Sleeping for {delay:.2f}s before next price batch...")
            await asyncio.sleep(delay)

    # Add metadata including top movers
    movers = analyze_movers(all_prices)

    # Use EST (US/Eastern) for display anchored to UTC
    now_utc = datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo

        now_est = now_utc.astimezone(ZoneInfo("US/Eastern"))
    except Exception:
        now_est = now_utc - timedelta(hours=4)  # Rough EST

    refreshed_at_str = now_est.strftime("%Y-%m-%d %I:%M %p EST")
    # Compact format for UI: 2026-04-16 01:49 EST
    compact_ts = now_est.strftime("%Y-%m-%d %I:%M EST")

    all_prices["_meta"] = {
        "refreshed_at": refreshed_at_str,
        "refreshed_at_est": compact_ts,
        "refreshed_at_iso": now_est.isoformat(),
        "total_tickers": len(all_prices),
        "with_price": sum(1 for t, d in all_prices.items() if d.get("price") and t != "_meta"),
        **movers,
    }

    log.info("-" * 50)
    # V28.1: Correctly calculate batch refresh success vs total universe
    batch_with_price = sum(1 for t in tickers if all_prices.get(t, {}).get("price"))
    log.info(f"Fetched {batch_with_price}/{len(tickers)} prices in this cycle")

    if movers["top_gainers"]:
        log.info(
            f'Top gainer: {movers["top_gainers"][0]["ticker"]} +{movers["top_gainers"][0]["change_pct"]:.1f}%'
        )
    if movers["top_losers"]:
        log.info(
            f'Top loser:  {movers["top_losers"][0]["ticker"]} {movers["top_losers"][0]["change_pct"]:.1f}%'
        )

    if not dry_run:
        # V24.6: Database Hygiene - Purge any entries older than 24 hours before saving
        now_ts = time.time()
        purged_prices = {
            t: d
            for t, d in all_prices.items()
            if t == "_meta" or (now_ts - d.get("timestamp", 0)) < 86400
        }

        # Write JSON (for audit/debugging)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(purged_prices, f, indent=2)
        log.info(f"Saved {OUT_JSON} (Purged {len(all_prices) - len(purged_prices)} stale entries)")

        # Write JS (for HTML terminal consumption)
        with open(OUT_JS, "w", encoding="utf-8") as f:
            f.write("// GIGACPO Live Prices - auto-generated by engine/live_prices.py\n")
            f.write("// DO NOT EDIT. Regenerate with: python engine/live_prices.py\n")
            f.write("window.LIVE_PRICES = ")
            json.dump(all_prices, f, separators=(",", ":"))
            f.write(";\n")
        log.info(f"Saved {OUT_JS}")

        # AUTO-SYNC to SFTP
        if not skip_sync:
            try:
                from remote_sync import RemoteSync

                rel_js = OUT_JS.relative_to(ROOT)
                RemoteSync.sync_file(OUT_JS)
            except Exception as e:
                log.error(f"Sync failed: {e}")
    else:
        log.info("[DRY RUN] Output not written")
        print(json.dumps(all_prices, indent=2)[:1000] + "\n...[truncated]")

    return all_prices


PRICE_TTL_SECONDS = 900


async def async_main():
    parser = argparse.ArgumentParser(description="GIGACPO Live Price Fetcher")
    parser.add_argument("--tickers", nargs="+", help="Specific tickers")
    parser.add_argument("--dry-run", action="store_true", help="Print, do not write")
    parser.add_argument("--force", action="store_true", help="Override cache")
    parser.add_argument("--skip-sync", action="store_true", help="Do not upload to SFTP")
    args = parser.parse_args()

    # V22.95: Global lock removed in favor of granular per-ticker TTL in async_run_fetch
    await async_run_fetch(
        tickers=args.tickers,
        force=args.force,
        dry_run=args.dry_run,
        skip_sync=args.skip_sync,
    )


if __name__ == "__main__":
    asyncio.run(async_main())
