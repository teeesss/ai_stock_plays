import time

from engine.email_market_synopsis import SovereignIntelligenceEngine
from engine.macro_aggregator import MacroAggregator


def test_lookback_filtering():
    """V28: Ensure articles older than the limit (36h/60h) are excluded via Aggregator."""
    agg = MacroAggregator()
    now = time.time()

    # 10 hours ago (Fresh)
    fresh_ts = now - (10 * 3600)
    # 72 hours ago (Old - beyond 36h/60h limits)
    old_ts = now - (72 * 3600)

    assert agg.is_fresh_enough(fresh_ts) == True
    assert agg.is_fresh_enough(old_ts) == False


def test_sector_data_loading():
    """Ensure SovereignIntelligenceEngine can identify AI and Semi tickers."""
    engine = SovereignIntelligenceEngine()

    # Check legit ticker logic (V28)
    assert engine.is_legit_ticker("NVDA") == True
    assert engine.is_legit_ticker("ARM") == True
    assert engine.is_legit_ticker("AI") == False  # Blocked noise
