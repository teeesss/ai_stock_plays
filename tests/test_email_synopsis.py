import pytest
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from engine.email_market_synopsis import MarketSynopsisEngine

def test_lookback_filtering():
    """Ensure items older than 36h are excluded."""
    engine = MarketSynopsisEngine()
    now = datetime.now()
    
    # ISO 8601 timestamps
    sample_news = [
        {"timestamp": (now - timedelta(hours=10)).isoformat(), "title": "Fresh News"},
        {"timestamp": (now - timedelta(hours=48)).isoformat(), "title": "Old News"}
    ]
    
    filtered = engine.filter_by_lookback(sample_news, hours=36)
    assert len(filtered) == 1
    assert filtered[0]["title"] == "Fresh News"

def test_sector_data_loading():
    """Ensure we can load data for both AI and Semi."""
    engine = MarketSynopsisEngine()
    data = engine.gather_data()
    
    assert "ai" in data
    assert "semi" in data
    # Basic smoke test - should have tickers if DBs exist
    assert len(data["ai"]["tickers"]) > 0 or os.path.exists("database/AI_MASTER_DATA.json")
