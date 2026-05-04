# tests/test_news_centralization.py
import asyncio
import time

import pytest

from engine.macro_aggregator import MacroAggregator


@pytest.mark.asyncio
async def test_freshness_gate_rejection():
    agg = MacroAggregator()
    # Mock an old article (1 year ago)
    old_ts = time.time() - (365 * 24 * 3600)
    is_fresh = agg.is_fresh_enough(old_ts)
    assert is_fresh is False, "Gate should reject articles from prior years"


@pytest.mark.asyncio
async def test_fetch_ticker_news_basic():
    agg = MacroAggregator()
    tickers = ["NVDA"]
    # Mock macro headlines to avoid full fetch
    macro = [
        {
            "title": "NVDA sets new record",
            "link": "http://test.com/1",
            "score": 90,
            "date": time.time(),
        }
    ]

    # This should fail if fetch_ticker_news is not implemented yet
    try:
        results = await agg.fetch_ticker_news(tickers, macro_headlines=macro)
        assert len(results) >= 1
        assert any("NVDA" in r["title"] for r in results)
    except AttributeError:
        pytest.fail("MacroAggregator has no attribute 'fetch_ticker_news'")


if __name__ == "__main__":
    asyncio.run(test_fetch_ticker_news_basic())
