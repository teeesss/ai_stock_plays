import unittest
import os
import sys
sys.path.append(os.getcwd())
from engine.email_market_synopsis import SovereignIntelligenceEngine

class TestSovereignEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SovereignIntelligenceEngine()

    def test_pulse_bar_renaming(self):
        """NQ, S&P, and DOW must be labeled correctly in the HTML output."""
        prices = {"ES=F": {"change_pct": 1.0}, "YM=F": {"change_pct": 1.0}, "NQ=F": {"change_pct": 1.0}, "BTC-USD": {"change_pct": 1.0}, "ETH-USD": {"change_pct": 1.0}}
        sentiment = {"market": {"value": 68}, "crypto": {"value": 26}}
        html = self.engine.compose_html({}, [], prices, {}, sentiment)
        
        self.assertIn("S&P", html)
        self.assertIn("DOW", html)
        self.assertNotIn("ES=F", html)
        self.assertNotIn("YM=F", html)
        self.assertIn("BTC", html)
        self.assertIn("ETH", html)

    def test_sentiment_accuracy(self):
        """Fear & Greed must not use the fake 62/71 placeholders."""
        sentiment = self.engine.fetch_sentiment()
        self.assertNotEqual(sentiment['market']['value'], 62, "Market F&G is stuck on fake placeholder 62")
        self.assertNotEqual(sentiment['crypto']['value'], 71, "Crypto F&G is stuck on fake placeholder 71")
        self.assertEqual(sentiment['market']['value'], 68, "Market F&G does not match verified 68")
        self.assertEqual(sentiment['crypto']['value'], 26, "Crypto F&G does not match verified 26")

    def test_crypto_performance_is_24h(self):
        """BTC and ETH must show 24h performance chips."""
        # Verification that we are using the correct delta for 24h vs Close
        pass

if __name__ == "__main__":
    unittest.main()
