from datetime import datetime, timezone

from engine.market_session import MarketSession


def test_weekend_stasis_detection():
    """V26.14: Logic check for Saturday/Sunday stasis."""
    session = MarketSession()

    # Saturday, April 25, 2026 (The current day)
    # 2026-04-25 is a Saturday
    sat_dt = datetime(2026, 4, 25, 12, 0, tzinfo=timezone.utc)
    assert session.is_market_stasis(dt_override=sat_dt) is True

    # Monday, April 27, 2026 (Active)
    mon_dt = datetime(2026, 4, 27, 14, 0, tzinfo=timezone.utc)  # 10 AM EST
    assert session.is_market_stasis(dt_override=mon_dt) is False


def test_sunday_night_futures_window():
    """Sunday 6 PM EST+ is NOT stasis."""
    session = MarketSession()
    # Sunday, April 26, 2026 @ 7 PM EST (23:00 UTC)
    sun_night = datetime(2026, 4, 26, 23, 0, tzinfo=timezone.utc)
    assert session.is_market_stasis(dt_override=sun_night) is False
