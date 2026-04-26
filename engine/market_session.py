"""
engine/market_session.py [V28]
========================
The Top of the Hierarchy for all Market Temporal Logic.
Unifies Weekend (Stasis) and Session (PRE/LIVE/AH/OVN) detection
to ensure ecosystem-wide consistency.
"""

import datetime
from datetime import timedelta, timezone

# V28: Hierarchy Leader Error Monitoring
try:
    from error_monitor import init_error_monitor
except ImportError:
    from engine.error_monitor import init_error_monitor
init_error_monitor()


class MarketSession:
    def __init__(self):
        pass

    def get_est_now(self, dt_override=None):
        """Returns the current time normalized to US/Eastern (EDT/EST) anchored to UTC."""
        if dt_override:
            if dt_override.tzinfo is None:
                # Assume naive is UTC for testing purposes if not specified
                dt_override = dt_override.replace(tzinfo=timezone.utc)
            now_utc = dt_override.astimezone(timezone.utc)
        else:
            now_utc = datetime.datetime.now(timezone.utc)

        try:
            from zoneinfo import ZoneInfo

            return now_utc.astimezone(ZoneInfo("US/Eastern"))
        except Exception:
            # Fallback for systems without zoneinfo (subtract 4 hours for EDT)
            return now_utc - timedelta(hours=4)

    def is_market_stasis(self, dt_override=None):
        """
        V26.14: Weekend Stasis Detector.
        Returns True if markets are completely dead (Sat/Sun before Sunday night futures).
        """
        now_est = self.get_est_now(dt_override)
        day = now_est.weekday()  # Mon=0, Sat=5, Sun=6
        hr = now_est.hour

        # Saturday (All day)
        if day == 5:
            return True

        # Sunday (Before 6 PM EST)
        if day == 6 and hr < 18:
            return True

        return False

    def get_market_session_label(self, symbol=None, dt_override=None):
        """
        Determines the current active session label for a given symbol.
        Returns: 'LIVE', 'PRE', 'AH', 'OVN', or 'CLOSED' (for weekend/night stasis).
        """
        now_est = self.get_est_now(dt_override)
        day = now_est.weekday()
        hr = now_est.hour
        mn = now_est.minute
        tm = hr * 100 + mn

        # 1. Crypto Override
        if symbol and symbol.upper().endswith("-USD"):
            return "LIVE"

        # 2. Weekend Stasis
        if self.is_market_stasis(dt_override):
            return "CLOSED"

        # 3. Sunday Night Futures (6 PM+)
        if day == 6 and hr >= 18:
            return "OVN"

        # 4. Standard US Market Hours (EST)
        # Premarket: 4:00 AM - 9:30 AM
        if 400 <= tm < 930:
            return "PRE"
        # Regular: 9:30 AM - 4:00 PM
        if 930 <= tm < 1600:
            return "LIVE"
        # After-Hours: 4:00 PM - 8:00 PM
        if 1600 <= tm < 2000:
            return "AH"
        # Overnight: 8:00 PM - 4:00 AM
        if tm >= 2000 or tm < 400:
            return "OVN"

        return "CLOSED"

    def is_market_active(self, dt_override=None):
        """General check if any form of active trading (including extended) is occurring."""
        label = self.get_market_session_label(dt_override=dt_override)
        return label in ["LIVE", "PRE", "AH", "OVN"]
