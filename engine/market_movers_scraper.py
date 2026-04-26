import asyncio
import json
import re
import sys
from pathlib import Path

from curl_cffi import requests

# Add engine to path
sys.path.append(str(Path(__file__).parent.parent / "engine"))
from yahoo_auth import get_valid_auth


async def scrape_yahoo_movers_html(mover_type="gainers"):
    cookie_dict, crumb, user_agent = await get_valid_auth()
    url = f"https://finance.yahoo.com/markets/stocks/{mover_type}/"

    headers = {
        "User-Agent": user_agent,
    }

    res = requests.get(url, headers=headers, cookies=cookie_dict, impersonate="chrome146")
    if res.status_code != 200:
        return []

    html = res.text

    # NEW: Specific table row pattern for Yahoo Finance tables
    # Tickers are often in <a> tags with class containing 'subtle-link' or inside 'data-symbol'
    # Actually, let's look for the specific link format inside the table
    # <a ... href="/quote/SYMBOL/" ...
    tickers = re.findall(r'href="/quote/([A-Z\.-]+)/"', html)

    # Filter and deduplicate
    unique_tickers = []
    seen = set()
    for t in tickers:
        # V24.8: Hardened Equity Filter - No Crypto, No Indices, No Futures
        # Skip BTC-USD, ETH-USD, etc.
        if "-" in t or t.endswith("=F") or t.startswith("^"):
            continue

        if t not in seen and t.isupper() and len(t) < 8:
            unique_tickers.append(t)
            seen.add(t)

    return unique_tickers[:20]


async def get_market_movers():
    try:
        gainers = await scrape_yahoo_movers_html("gainers")
        losers = await scrape_yahoo_movers_html("losers")
        return {"gainers": gainers, "losers": losers}
    except Exception:
        return {"gainers": [], "losers": []}


if __name__ == "__main__":
    movers = asyncio.run(get_market_movers())
    print(json.dumps(movers))
