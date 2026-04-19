
import unittest
import sys
import os
from pathlib import Path

# Add engine to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../engine')))
from intelligence_engine import IntelligenceEngine

class TestIntelligenceEngine(unittest.TestCase):
    def test_scores_are_dynamic(self):
        """Verify that scores are no longer hardcoded defaults."""
        
        # Scenario 1: A "God Tier" stock (Small cap, huge upside, high buzz)
        stock_a = {
            "symbol": "GOD",
            "pe26": 12,
            "upside": 1.5, # 150%
            "mcapB": 0.1,
            "buzz_7d": 500,
            "news_count": 50,
            "analysts": 1,
            "inst_pct": 2,
            "short_pct": 1,
            "perf1y": 250.0,
            "recent_7d": [1, 1, 1, 1, 1, 1, 1]
        }
        
        # Scenario 2: A "Mid" stock
        stock_mid = {
            "symbol": "MID",
            "pe26": 25,
            "upside": 0.2, # 20%
            "mcapB": 10.0,
            "buzz_7d": 50,
            "news_count": 5,
            "analysts": 8,
            "inst_pct": 40,
            "short_pct": 5,
            "perf1y": 15.0,
            "recent_7d": [1, 0, 1, 0, 1, 0, 1]
        }

        # Scenario 3: A "Bloated" stock (Huge cap, no upside, no buzz, heavily covered)
        stock_b = {
            "symbol": "BLOAT",
            "pe26": 80,
            "upside": 0.02, # 2%
            "mcapB": 2000.0,
            "buzz_7d": 1,
            "news_count": 1,
            "analysts": 50,
            "inst_pct": 85,
            "short_pct": 15,
            "perf1y": -5.0,
            "recent_7d": [0,0,0,0,0,0,0]
        }
        
        data_map = {
            "GOD": stock_a,
            "MID": stock_mid,
            "BLOAT": stock_b
        }
        
        stats_list = IntelligenceEngine.prepare_dataset_for_scoring(data_map)
        engine = IntelligenceEngine(stats_list)
        
        scores_a = engine.calculate_ticker_score(stock_a)
        scores_mid = engine.calculate_ticker_score(stock_mid)
        scores_b = engine.calculate_ticker_score(stock_b)
        
        print(f"\nGOD Alpha: {scores_a['alpha']} | Risk: {scores_a['risk']} | Hidden: {scores_a['hidden']}")
        print(f"MID Alpha: {scores_mid['alpha']} | Risk: {scores_mid['risk']} | Hidden: {scores_mid['hidden']}")
        print(f"BLOAT Alpha: {scores_b['alpha']} | Risk: {scores_b['risk']} | Hidden: {scores_b['hidden']}")

        # Check that they aren't hardcoded defaults (legacy 8.2/3/5)
        self.assertNotEqual(scores_a['alpha'], 8.2)
        
        # Comparisons
        # 1. Alpha: GOD > MID > BLOAT
        self.assertGreater(scores_a['alpha'], scores_mid['alpha'])
        self.assertGreater(scores_mid['alpha'], scores_b['alpha'])
        
        # 2. Hiddenness: GOD should be more hidden than BLOAT (BLOAT has many analysts and news)
        self.assertGreater(scores_a['hidden'], scores_b['hidden'])
        
        # 3. Risk: BLOAT should be riskier due to high PE and low growth/high shorts (if applicable)
        # Note: Risk in engine also considers FUD (news > 5 and mom < 0)
        self.assertGreater(scores_b['risk'], scores_a['risk'])

if __name__ == '__main__':
    unittest.main()
