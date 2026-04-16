import unittest
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Adjust path to import from engine
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / 'engine'))


class TestTerminalUpdates(unittest.TestCase):
    def setUp(self):
        self.master_data_path = ROOT / 'database' / 'CPO_MASTER_DATA.json'
        self.live_prices_json = ROOT / 'database' / 'live_prices.json'
        self.live_prices_js = ROOT / 'database' / 'live_prices.js'

    def test_exchange_mapping_logic(self):
        """Verify the exchange abbreviation mapping."""
        # This tests the logic we intend to implement
        from engine.live_prices import get_exchange_abbr
        
        test_cases = {
            "NasdaqGS": "NASDAQ",
            "Nasdaq": "NASDAQ",
            "New York Stock Exchange": "NYSE",
            "NYSE": "NYSE",
            "OTC Markets OTCPK": "OTC",
            "PNK": "OTC",
            "BATS": "BATS",
            "YHD": "HKG"
        }
        
        for input_name, expected in test_cases.items():
            with self.subTest(name=input_name):
                self.assertEqual(get_exchange_abbr(input_name), expected)

    def test_live_prices_has_est_timestamp(self):
        """Verify that live_prices.json contains an EST timestamp."""
        if not self.live_prices_json.exists():
            self.skipTest("live_prices.json not found")
            
        with open(self.live_prices_json, 'r') as f:
            data = json.load(f)
            
        self.assertIn('_meta', data)
        self.assertIn('refreshed_at_est', data['_meta'])
        est_str = data['_meta']['refreshed_at_est']
        self.assertIn('EST', est_str)

    def test_instant_sync_orchestration(self):
        """Verify that x_intel_instant_sync.py includes live_prices.py in its sequence."""
        sync_file = ROOT / 'engine' / 'x_intel_instant_sync.py'
        with open(sync_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if live_prices is mentioned in the sync sequence
        self.assertIn('live_prices.py', content, "live_prices.py should be triggered at the end of instant sync")

if __name__ == '__main__':
    unittest.main()
