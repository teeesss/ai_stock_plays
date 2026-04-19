import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../engine')))

from intelligence_engine import IntelligenceEngine
from data_standardizer import DataStandardizer

class TestIntelligenceEngine(unittest.TestCase):
    def setUp(self):
        self.mock_data = {
            "NVDA": {"pe26": 30, "mcapB": 3000, "perf1y": 150, "buzz_7d": 100, "news_count": 20, "upside": 10},
            "AAPL": {"pe26": 28, "mcapB": 3000, "perf1y": 20, "buzz_7d": 50, "news_count": 5, "upside": 5},
            "SIVE": {"pe26": 10, "mcapB": 0.5, "perf1y": 10, "buzz_7d": 2, "news_count": 1, "upside": 50}
        }
        self.stats_list = IntelligenceEngine.prepare_dataset_for_scoring(self.mock_data)
        self.engine = IntelligenceEngine(self.stats_list)

    def test_alpha_logic(self):
        # SIVE should have high Alpha due to low P/E, low market cap, and high upside
        sive_scores = self.engine.calculate_ticker_score(self.mock_data["SIVE"])
        # NVDA should have decent Alpha due to high buzz/news
        nvda_scores = self.engine.calculate_ticker_score(self.mock_data["NVDA"])
        
        self.assertGreater(sive_scores['alpha'], 5.0)
        self.assertGreater(nvda_scores['alpha'], 5.0)

    def test_hiddenness_logic(self):
        # SIVE is small cap and low news -> should be more hidden than NVDA
        sive_scores = self.engine.calculate_ticker_score(self.mock_data["SIVE"])
        nvda_scores = self.engine.calculate_ticker_score(self.mock_data["NVDA"])
        self.assertGreater(sive_scores['hidden'], nvda_scores['hidden'])

class TestDataStandardizer(unittest.TestCase):
    def test_bucket_normalization(self):
        self.assertEqual(DataStandardizer.normalize_bucket("AI WATCHLIST"), "AI Watchlist")
        self.assertEqual(DataStandardizer.normalize_bucket("SEMICONDUCTORS"), "Semiconductors")
    
    def test_exchange_normalization(self):
        self.assertEqual(DataStandardizer.normalize_exchange("NasdaqGS"), "NASDAQ")
        self.assertEqual(DataStandardizer.normalize_exchange("OTC Markets"), "OTC")

if __name__ == '__main__':
    unittest.main()
