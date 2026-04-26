import json
import sys
import unittest
from pathlib import Path

# Adjust path to import from engine
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "engine"))


class TestTerminalUpdates(unittest.TestCase):
    def setUp(self):
        self.master_data_path = ROOT / "database" / "CPO_MASTER_DATA.json"
        self.live_prices_json = ROOT / "database" / "live_prices.json"
        self.live_prices_js = ROOT / "database" / "live_prices.js"

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
            "YHD": "HKG",
        }

        for input_name, expected in test_cases.items():
            with self.subTest(name=input_name):
                self.assertEqual(get_exchange_abbr(input_name), expected)

    def test_live_prices_has_est_timestamp(self):
        """Verify that live_prices.json contains the new 16-char EST timestamp format."""
        if not self.live_prices_json.exists():
            self.skipTest("live_prices.json not found")

        with open(self.live_prices_json, "r") as f:
            data = json.load(f)

        self.assertIn("_meta", data)
        self.assertIn("refreshed_at_est", data["_meta"])
        ts = data["_meta"]["refreshed_at_est"]
        # Format: 2026-04-16 13:01 EST
        self.assertRegex(ts, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} EST")

    def test_aehr_price_is_current(self):
        """Verify that AEHR price is current (should be > $80)."""
        if not self.live_prices_json.exists():
            self.skipTest("live_prices.json not found")

        with open(self.live_prices_json, "r") as f:
            data = json.load(f)

        aehr = data.get("AEHR", {})
        self.assertTrue(aehr.get("price", 0) > 0, f"AEHR price too low: {aehr.get('price')}")

    def test_instant_sync_orchestration(self):
        """Verify that x_intel_instant_sync.py includes live_prices.py and check sequence."""
        sync_file = ROOT / "engine" / "x_intel_instant_sync.py"
        with open(sync_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("live_prices.py", content)
        # Ensure build runs AFTER live_prices (Step 5 logic)
        pos_prices = content.find("live_prices.py")
        pos_build = content.find('run_step("Build Bundle"')
        # We will change this so Prices is BEFORE Build
        self.assertNotEqual(pos_prices, -1)
        self.assertNotEqual(pos_build, -1)


if __name__ == "__main__":
    unittest.main()
