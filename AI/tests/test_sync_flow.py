import unittest
import os
import time
from pathlib import Path

class TestAISyncFlow(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.prices_js = self.root / "database" / "live_prices.js"
        self.master_js = self.root / "database" / "dashboard_data.js"

    def test_sync_updates_files(self):
        """Verify that AI sync updates the target local JS files."""
        t_start = time.time()
        
        # We assume the sync script is AI/engine/sync_ai_watchlist.py
        # For TDD, this test should fail because the script doesn't exist or isn't run.
        sync_script = self.root / "engine" / "sync_ai_watchlist.py"
        self.assertTrue(sync_script.exists(), "AI Sync script missing")
        
        # Check mtimes
        self.assertGreater(self.prices_js.stat().st_mtime, t_start - 3600, "Prices stale")

if __name__ == "__main__":
    unittest.main()
