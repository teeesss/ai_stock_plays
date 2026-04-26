import asyncio
import sys
from pathlib import Path

# Add root to sys.path
root = Path(__file__).parent.parent
sys.path.append(str(root))
sys.path.append(str(root / "engine"))

try:
    from engine.email_market_synopsis import SovereignIntelligenceEngine
    from engine.live_prices import async_run_fetch
except ImportError:
    from email_market_synopsis import SovereignIntelligenceEngine
    from live_prices import async_run_fetch


async def test_session_accuracy():
    """
    Spot check tickers for session accuracy.
    """
    engine = SovereignIntelligenceEngine()
    test_tickers = ["ALAB", "POET", "CIFR", "NVDA"]

    print(f"--- SESSION ACCURACY AUDIT ({engine.now.strftime('%H:%M:%S EST')}) ---")

    # 1. Fetch fresh data
    print(f"Fetching fresh data for {test_tickers}...")
    prices = await async_run_fetch(tickers=test_tickers, force=True, skip_sync=True)

    # 2. Analyze each ticker
    for sym in test_tickers:
        p_data = prices.get(sym, {})
        if not p_data:
            print(f"[{sym}] FAILED: No data returned from fetcher.")
            continue

        # Get regular price (Yesterday's close if PRE)
        reg_price = p_data.get("price")
        reg_pct = p_data.get("change_pct")

        # Get session data via Engine logic
        final_price, final_pct, final_sess = engine.get_session_data(p_data, sym)

        # Check if ext_price is present in raw data
        ext_price = p_data.get("ext_price")
        ext_pct = p_data.get("ext_pct")
        ext_type = p_data.get("ext_type")

        print(f"[{sym}]")
        print(f"  - Yahoo State:  {p_data.get('exchange')} (ext_type: {ext_type})")
        print(f"  - reg_price:    ${reg_price:.2f} ({reg_pct:+.2f}%)")
        print(f"  - ext_price:    ${ext_price if ext_price is not None else 'N/A'}")
        print(f"  - ext_pct:      {ext_pct if ext_pct is not None else 'N/A'}%")
        print(f"  - Engine Label: {final_sess}")
        print(f"  - Final Render: ${final_price:.2f} ({final_pct:+.2f}%)")

        # VERIFICATION
        if engine.get_market_session(sym) == "PRE" and ext_price is not None:
            if final_price == reg_price and final_price != ext_price:
                print("  ❌ BUG DETECTED: Showing Yesterday's Close instead of Premarket!")
            elif final_price == ext_price:
                print("  ✅ SUCCESS: Rendered matches Active Session price.")
            else:
                print(f"  ⚠️ Mixed state: {final_price} != {ext_price}")
        print("-" * 30)


if __name__ == "__main__":
    asyncio.run(test_session_accuracy())
