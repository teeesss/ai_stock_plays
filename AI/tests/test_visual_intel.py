import unittest
import os
import json
from pathlib import Path

class TestAIVisualIntel(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.dashboard_data_js = self.root / "database" / "dashboard_data.js"

    def test_visual_mentions_present(self):
        """Verify that AI dashboard data includes visual OCR hit metadata."""
        with open(self.dashboard_data_js, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('"visual_mentions"', content, "AI data missing visual_mentions hits")

if __name__ == "__main__":
    unittest.main()
