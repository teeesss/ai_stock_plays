import unittest
import os
import sys

# Ensure engine path is visible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Red - Expecting Import Error until implemented
try:
    from engine.news_fetcher import YahooNewsFetcher
except ImportError:
    YahooNewsFetcher = None

class TestYahooNewsFetcher(unittest.TestCase):
    def test_fetch_batch_structure(self):
        if YahooNewsFetcher is None:
            self.fail("YahooNewsFetcher module not found - implementation missing.")
            
        fetcher = YahooNewsFetcher()
        tickers = ["NVDA"] # High liquidity guaranteed news
        results = fetcher.fetch_batch(tickers)
        
        self.assertIn("NVDA", results)
        if len(results["NVDA"]) > 0:
            self.assertIn("vibe_score", results["NVDA"][0])
            self.assertIn("title", results["NVDA"][0])
            self.assertIn("link", results["NVDA"][0])
            
        # Stealth check
        self.assertTrue(len(fetcher.headers["User-Agent"]) > 10)

if __name__ == "__main__":
    unittest.main()
