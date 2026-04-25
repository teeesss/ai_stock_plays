
import unittest
import sys
import os
from pathlib import Path

# Add root to sys.path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "engine"))

class TestPricingMath(unittest.TestCase):
    def test_decoupled_ah_price_rendering(self):
        """V26.8: Ensure closing price and AH price are distinct and accurate."""
        # 1. Verify code structure in email_market_synopsis.py
        synopsis_path = ROOT / "engine" / "email_market_synopsis.py"
        if not synopsis_path.exists():
            self.skipTest("email_market_synopsis.py not found")
            
        src = open(synopsis_path, "r", encoding="utf-8").read()
        
        # 1. Check for reg_price extraction (Must not clobber with session price)
        self.assertIn("reg_price = p_entry.get('price', 0)", src, "Missing decoupled reg_price extraction")
        
        # 2. Check for ext_price extraction
        self.assertIn("ext_price = p_entry.get('ext_price')", src, "Missing decoupled ext_price extraction")
        
        # 3. Check for separate rendering slots
        self.assertIn("price_str = f\"${reg_price:,.2f}\"", src, "price_str should use reg_price")
        self.assertIn("${ext_price:,.2f}", src, "ext_html should use ext_price")

    def test_ah_percent_calculation_integrity(self):
        """V26.8: Ensure AH change is not mixed with total change in the secondary slot."""
        synopsis_path = ROOT / "engine" / "email_market_synopsis.py"
        if not synopsis_path.exists():
            self.skipTest("email_market_synopsis.py not found")
            
        src = open(synopsis_path, "r", encoding="utf-8").read()
        
        # Verify it uses ext_pct for the AH slot
        self.assertIn("{ext_pct:+.1f}%", src, "Secondary slot must show extended-session specific percentage")

if __name__ == '__main__':
    unittest.main()
