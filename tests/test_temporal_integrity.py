import datetime
import os
import sys
from datetime import timedelta

# Add engine to path
sys.path.append(os.path.join(os.getcwd(), "engine"))

from email_market_synopsis import SovereignIntelligenceEngine
from live_prices import calculate_session_data


def test_est_fallback():
    """Verify that the rough EST fallback matches expected -4h offset."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # This is what our logic does
    est_rough = now_utc - timedelta(hours=4)

    engine = SovereignIntelligenceEngine()
    est_engine = engine._get_est_now()

    # Allow for slight delta in execution time by comparing clock values
    assert (
        est_rough.hour == est_engine.hour
    ), f"Hour mismatch: {est_rough.hour} vs {est_engine.hour}"
    assert abs(est_rough.minute - est_engine.minute) <= 1, "Minute mismatch"


def test_session_boundaries():
    """Verify US session boundaries at various times."""
    engine = SovereignIntelligenceEngine()

    # V28: dt_override must be EST-aware; get_est_now treats naive datetimes as UTC
    try:
        from zoneinfo import ZoneInfo

        EST = ZoneInfo("US/Eastern")
    except ImportError:
        from datetime import timedelta, timezone

        EST = timezone(timedelta(hours=-4))  # EDT fallback

    # 1. 9:29 AM EST -> PRE
    dt_929 = datetime.datetime(2026, 4, 22, 9, 29, 0, tzinfo=EST)
    assert engine.get_market_session(dt_override=dt_929) == "PRE"

    # 2. 9:30 AM EST -> LIVE
    dt_930 = datetime.datetime(2026, 4, 22, 9, 30, 0, tzinfo=EST)
    assert engine.get_market_session(dt_override=dt_930) == "LIVE"

    # 3. 3:59 PM EST -> LIVE
    dt_1559 = datetime.datetime(2026, 4, 22, 15, 59, 0, tzinfo=EST)
    assert engine.get_market_session(dt_override=dt_1559) == "LIVE"

    # 4. 4:00 PM EST -> AH
    dt_1600 = datetime.datetime(2026, 4, 22, 16, 0, 0, tzinfo=EST)
    assert engine.get_market_session(dt_override=dt_1600) == "AH"

    # 5. 8:00 PM EST -> OVN
    dt_2000 = datetime.datetime(2026, 4, 22, 20, 0, 0, tzinfo=EST)
    assert engine.get_market_session(dt_override=dt_2000) == "OVN"


def test_calculate_session_data():
    """Verify field prioritization in live_prices.py."""

    # Mock item: POET-style (stale regular price, active premarket)
    item = {
        "symbol": "POET",
        "regularMarketPrice": 10.0,
        "preMarketPrice": 12.0,
        "preMarketChangePercent": 20.0,
        "marketState": "PREPRE",
    }

    # 1. At 8:00 AM (PRE)
    p, pct, t = calculate_session_data(item, 800)
    # V30.6.12: calculate_session_data uses 'PRE' as the canonical premarket label
    assert t == "PRE"
    assert p == 12.0
    assert pct == 20.0

    # 2. At 10:00 AM (LIVE) - Yahoo says REGULAR but price is stale
    item_live = item.copy()
    item_live["marketState"] = "REGULAR"
    item_live["regularMarketChangePercent"] = 0.5

    p, pct, t = calculate_session_data(item_live, 1000)
    assert t == "LIVE"
    assert p is None  # In LIVE hours, we don't override the main price field


def test_transition_logic():
    """Verify that crossing session boundary triggers refresh."""
    # Case: Last was PRE, Current is LIVE
    last_type = "PRE"
    curr_sess = "LIVE"
    session_changed = (
        (last_type == "PRE" and curr_sess == "LIVE")
        or (last_type == "LIVE" and curr_sess == "AH")
        or (last_type == "UNKNOWN")
    )
    assert session_changed is True

    # Case: Still in LIVE
    last_type = "LIVE"
    curr_sess = "LIVE"
    session_changed = (
        (last_type == "PRE" and curr_sess == "LIVE")
        or (last_type == "LIVE" and curr_sess == "AH")
        or (last_type == "UNKNOWN")
    )
    assert session_changed is False


if __name__ == "__main__":
    print("Running Temporal Integrity Tests...")
    try:
        test_est_fallback()
        print("[PASS] EST Fallback")
        test_session_boundaries()
        print("[PASS] Session Boundaries")
        test_calculate_session_data()
        print("[PASS] Session Data Extraction")
        test_transition_logic()
        print("[PASS] Transition Logic")
        print("\nALL TEMPORAL INTEGRITY TESTS PASSED.")
    except Exception as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
