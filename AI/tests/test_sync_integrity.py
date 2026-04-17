import unittest
import os
import json
from pathlib import Path

class TestAISyncIntegrity(unittest.TestCase):
    def setUp(self):
        # ROOT is AI/
        self.root = Path(__file__).parent.parent
        self.ai_db = self.root / "database"
        self.live_prices_js = self.ai_db / "live_prices.js"
        self.dashboard_data_js = self.ai_db / "dashboard_data.js"
        self.news_module_js = self.ai_db / "YAHOO_NEWS_MODULE.js"

    def test_live_prices_exists(self):
        """Verify AI live_prices.js artifact exists."""
        self.assertTrue(self.live_prices_js.exists(), "database/live_prices.js missing")

    def test_dashboard_data_exists(self):
        """Verify AI dashboard_data.js artifact exists."""
        self.assertTrue(self.dashboard_data_js.exists(), "database/dashboard_data.js missing")

    def test_news_module_exists(self):
        """Verify AI YAHOO_NEWS_MODULE.js artifact exists."""
        self.assertTrue(self.news_module_js.exists(), "database/YAHOO_NEWS_MODULE.js missing")

    def test_live_prices_content(self):
        """Verify live_prices.js has window.LIVE_PRICES assignment."""
        with open(self.live_prices_js, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("window.LIVE_PRICES =", content)

if __name__ == "__main__":
    unittest.main()
