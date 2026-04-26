"""
GIGACPO Intelligence Engine (V28)
Advanced scoring module using percentile normalization and weighted hazard detection.
Design: Individual module for cross-terminal deployment.
"""


class IntelligenceEngine:
    def __init__(self, full_dataset_stats=None):
        """
        full_dataset_stats: List of dicts for all tickers in the universe.
        Used for percentile normalization.
        """
        self.stats = full_dataset_stats or []

    def get_percentile(self, val, key, reverse=False):
        """Calculates rank of val within the full dataset for a specific key."""
        if val is None:
            return 0.5
        all_vals = [s.get(key) for s in self.stats if s.get(key) is not None]
        if not all_vals:
            return 0.5

        sorted_vals = sorted(all_vals)
        if len(sorted_vals) <= 1:
            return 1.0  # Solo winner

        # Using interpolation-style rank to prevent 0.0 scores in small sets
        rank = sum(1 for v in sorted_vals if val > v)
        pct = rank / (len(sorted_vals) - 1)

        return (1.0 - pct) if reverse else pct

    def calculate_ticker_score(self, ticker_stats):
        """
        Calculates Alpha, Risk, and Hiddenness (1-10) using V3 Core/Velocity Logic.
        Core (80%): Value + Runway
        Velocity (20%): Discovery + Momentum
        """
        # --- CORE FUNDAMENTALS (80% OF BASE) ---
        pe = ticker_stats.get("pe26") or 50
        upside = ticker_stats.get("upside") or 0
        mcap = ticker_stats.get("mcapB") or 100

        # Value Pillar (40%)
        # Inverse P/E + Analyst Upside
        alpha_val = (
            self.get_percentile(pe, "pe26", reverse=True) * 0.20
            + self.get_percentile(upside, "upside") * 0.20
        )

        # Runway Pillar (40%)
        # Smaller companies have higher expansion 'alpha'
        alpha_runway = self.get_percentile(mcap, "mcapB", reverse=True) * 0.40

        # --- VELOCITY BOOSTERS (20% OF BASE) ---
        total_discovery = ticker_stats.get("total_discovery") or 0
        alpha_discovery = self.get_percentile(total_discovery, "total_discovery") * 0.10

        recent_7d = ticker_stats.get("recent_7d") or []
        mom = (ticker_stats.get("perf1y") or 0) + (sum(recent_7d) * 10)
        alpha_mom = self.get_percentile(mom, "momentum_sum") * 0.10

        # Base Total (1.0 to 10.0 range)
        base_score = (alpha_val + alpha_runway + alpha_discovery + alpha_mom) * 10

        # --- THE KICKERS (ADDITIVE BONUSES) ---
        kicker_bonus = 0
        # Deep Value Kicker: PE < 15 and Upside > 40%
        if pe < 15 and upside > 40:
            kicker_bonus += 1.2
        # Viral Discovery Kicker: Massive news/buzz spike
        if total_discovery > 50:
            kicker_bonus += 0.8

        # 13F Conviction Boost (V20 Parity)
        conviction_count = ticker_stats.get("conviction_count") or 0
        conviction_boost = conviction_count * 1.5  # JS equivalent (+15 on 100-scale)

        alpha_score = round(base_score + kicker_bonus + conviction_boost, 1)
        alpha_score = max(1.0, min(10.0, alpha_score))

        # 2. HIDDENNESS Pillars (Inverse Discovery)
        h_analysts = (
            self.get_percentile(ticker_stats.get("analysts"), "analysts", reverse=True) * 0.40
        )
        h_inst = self.get_percentile(ticker_stats.get("inst_pct"), "inst_pct", reverse=True) * 0.30
        h_noise = self.get_percentile(total_discovery, "total_discovery", reverse=True) * 0.30
        hidden_score = round((h_analysts + h_inst + h_noise) * 10, 1)
        hidden_score = max(1.0, min(10.0, hidden_score))

        # 3. RISK Pillars (Valuation + Short Hazard)
        r_val = self.get_percentile(pe, "pe26") * 0.40
        r_short = self.get_percentile(ticker_stats.get("short_pct"), "short_pct") * 0.40

        # Hazard check: Falling momentum + High Discovery
        is_hazard = 1.0 if (total_discovery > 10 and mom < 0) else 0.5
        r_fud = is_hazard * 0.20
        risk_score = round((r_val + r_short + r_fud) * 10, 1)
        risk_score = max(1.0, min(10.0, risk_score))

        return {"alpha": alpha_score, "risk": risk_score, "hidden": hidden_score}

    @staticmethod
    def prepare_dataset_for_scoring(all_data_map):
        """Helper to transform raw dashboard dict into flat stats list for normalized scoring."""
        stats_list = []
        for symbol, entry in all_data_map.items():
            # This follows the expected schema for calculate_ticker_score
            item = {
                "symbol": symbol,
                "pe26": entry.get("pe26"),
                "upside": entry.get("upside"),
                "mcapB": entry.get("mcapB"),
                "total_discovery": entry.get("total_discovery") or 0,
                "perf1y": entry.get("perf1y", 0),
                "recent_7d": entry.get("recent_7d_list") or [],
                "momentum_sum": (entry.get("perf1y") or 0)
                + (sum(entry.get("recent_7d_list") or []) * 10),
                "analysts": entry.get("analysts"),
                "inst_pct": entry.get("inst_pct"),
                "short_pct": entry.get("short_pct"),
                "conviction_count": entry.get("conviction_count", 0),
            }
            stats_list.append(item)
        return stats_list
