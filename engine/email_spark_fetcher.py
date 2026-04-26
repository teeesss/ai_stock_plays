"""
engine/email_spark_fetcher.py
============================
Sidecar data fetcher for the GIGACPO Email System.
Fetches 15m interval chart data for sparkline generation.
Does NOT affect primary live_prices.py logic or production terminal state.
"""

import asyncio
import json
import logging

# Import auth and config from primary engine
import sys
import time
from pathlib import Path

from curl_cffi import requests

sys.path.append(str(Path(__file__).parent))
from yahoo_auth import get_valid_auth

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("email_spark")

ROOT = Path(__file__).parent.parent
OUT_JSON = ROOT / "database" / "email_sparklines.json"


async def fetch_sparkline(symbol: str, client, crumb: str):
    """Fetches 1-day chart data with 15m intervals."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=15m&range=1d&crumb={crumb}"

    try:
        res = client.get(url, timeout=10)
        if res.status_code != 200:
            log.error(f"Yahoo Spark Error: {symbol} -> {res.status_code}")
            return None

        data = res.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            log.error(f"No result in Yahoo chart for {symbol}")
            return None

        chart = result[0]
        indicators = chart.get("indicators", {})

        # Try Adjusted Close first
        adj_data = indicators.get("adjclose", [{}])[0]
        closes = adj_data.get("adjclose", [])

        # Fallback to standard Close
        if not closes:
            quote_data = indicators.get("quote", [{}])[0]
            closes = quote_data.get("close", [])

        # Filter out None values
        valid_points = [p for p in closes if p is not None]
        if not valid_points:
            log.warning(f"No valid points for {symbol}")
            return None

        # Sub-sample to ~30 points for clean rendering
        step = max(1, len(valid_points) // 30)
        return valid_points[::step]

    except Exception as e:
        log.error(f"Error fetching spark for {symbol}: {e}")
        return None


async def run_spark_fetch(tickers: list[str], force: bool = False):
    """Main entry point for email system to refresh spark data with 15m TTL."""
    # V22.96: Granular 15-Minute Stasis Protocol
    existing = {}
    if OUT_JSON.exists():
        try:
            with open(OUT_JSON, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except:
            pass

    # Filter for stale tickers only
    now_ts = time.time()
    stale_tickers = []
    if force:
        stale_tickers = tickers
    else:
        for t in tickers:
            # We store as { t: { "points": [...], "ts": ... } }
            entry = existing.get(t, {})
            if isinstance(entry, list):  # Legacy format fix
                stale_tickers.append(t)
                continue

            ts = entry.get("ts", 0)
            if (now_ts - ts) >= 900:  # 15 mins
                stale_tickers.append(t)

    if not stale_tickers:
        log.info("[CACHE] All sparklines are within 15m TTL. Skipping sidecar fetch.")
        return existing

    log.info(f"Refreshing sparklines for {len(stale_tickers)} stale tickers...")

    cookie_dict, crumb, user_agent = await get_valid_auth()
    client = requests.Session(impersonate="chrome146")
    client.headers.update({"User-Agent": user_agent})
    client.cookies.update(cookie_dict)

    results = existing.copy()
    for t in stale_tickers:
        points = await fetch_sparkline(t, client, crumb)
        if points:
            results[t] = {"points": points, "ts": time.time()}
            log.info(f"  Captured {len(points)} points for {t}")

    # Save to isolated JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    log.info(f"Sparklines saved to {OUT_JSON}")
    return results


if __name__ == "__main__":
    # Test run with sample tickers
    import time

    asyncio.run(run_spark_fetch(["AAPL", "TSLA", "NVDA", "BTC-USD"], force=True))
