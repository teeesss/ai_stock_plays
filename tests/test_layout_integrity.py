import unittest
import re
import os
from pathlib import Path

class TestLayoutIntegrity(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.preview_path = self.root / "database" / "synopsis_preview.html"
        
        if not self.preview_path.exists():
             # Try to generate it if missing (minimal run)
             os.system("python engine/email_market_synopsis.py --tickers NVDA")
             
    def test_no_line_breaks_in_movers(self):
        """Rule: Performance mover rows must NEVER contain <br/> tags."""
        with open(self.preview_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Target the mover-col content
        mover_sections = re.findall(r'<td class="mover-col".*?>(.*?)</td>', content, re.DOTALL)
        for section in mover_sections:
            # We allow <br/> in the header/container but NOT inside the individual ticker rows
            # The current buggy code puts <br/> inside perf-item
            perf_items = re.findall(r'<div class="perf-item".*?>(.*?)</div>', section, re.DOTALL)
            for item in perf_items:
                self.assertNotIn("<br", item.lower(), f"Line break found in ticker row: {item}")

    def test_nowrap_enforcement(self):
        """Rule: CSS must contain white-space:nowrap for ticker rows."""
        with open(self.preview_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertIn("white-space:nowrap", content.replace(" ", ""), "CSS missing white-space:nowrap enforcement")

if __name__ == "__main__":
    unittest.main()
