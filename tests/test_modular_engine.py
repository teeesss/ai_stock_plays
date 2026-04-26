import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../engine")))

from data_standardizer import DataStandardizer
from intelligence_engine import IntelligenceEngine


class TestIntelligenceEngine(unittest.TestCase):
    def setUp(self):
        self.mock_data = {
            "NVDA": {
                "pe26": 30,
                "mcapB": 3000,
                "perf1y": 150,
                "upside": 10,
                "total_discovery": 100,
                "analysts": 45,
                "inst_pct": 85,
                "short_pct": 1,
            },
            "AAPL": {
                "pe26": 28,
                "mcapB": 3000,
                "perf1y": 20,
                "upside": 5,
                "total_discovery": 50,
                "analysts": 40,
                "inst_pct": 60,
                "short_pct": 0.5,
            },
            "SIVE": {
                "pe26": 10,
                "mcapB": 0.5,
                "perf1y": 10,
                "upside": 50,
                "total_discovery": 2,
                "analysts": 1,
                "inst_pct": 5,
                "short_pct": 10,
            },
        }
        self.stats_list = IntelligenceEngine.prepare_dataset_for_scoring(self.mock_data)
        self.engine = IntelligenceEngine(self.stats_list)

    def test_alpha_logic(self):
        # SIVE should have high Alpha due to low P/E, low market cap, and high upside
        sive_scores = self.engine.calculate_ticker_score(self.mock_data["SIVE"])
        # NVDA should have decent Alpha due to high buzz/news
        nvda_scores = self.engine.calculate_ticker_score(self.mock_data["NVDA"])

        self.assertGreater(sive_scores["alpha"], 5.0)
        self.assertGreater(nvda_scores["alpha"], 5.0)

    def test_hiddenness_logic(self):
        # SIVE is small cap and low news -> should be more hidden than NVDA
        sive_scores = self.engine.calculate_ticker_score(self.mock_data["SIVE"])
        nvda_scores = self.engine.calculate_ticker_score(self.mock_data["NVDA"])
        self.assertGreater(sive_scores["hidden"], nvda_scores["hidden"])


class TestDataStandardizer(unittest.TestCase):
    def test_bucket_normalization(self):
        self.assertEqual(DataStandardizer.normalize_bucket("AI WATCHLIST"), "AI Watchlist")
        self.assertEqual(DataStandardizer.normalize_bucket("SEMICONDUCTORS"), "Semiconductors")

    def test_exchange_normalization(self):
        self.assertEqual(DataStandardizer.normalize_exchange("NasdaqGS"), "NASDAQ")
        self.assertEqual(DataStandardizer.normalize_exchange("OTC Markets"), "OTC")


if __name__ == "__main__":
    unittest.main()
