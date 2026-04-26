import os
import sys
import unittest
from pathlib import Path


class TestHeaderAesthetic(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.preview_path = self.root / "database" / "synopsis_preview.html"

        # Ensure we have a fresh preview
        if not self.preview_path.exists():
            print("Generating preview...")
            os.system(f"{sys.executable} engine/email_market_synopsis.py --tickers NVDA")

    def test_gradient_background_exists(self):
        """Rule: Wrap must have a linear-gradient background."""
        with open(self.preview_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("linear-gradient", content, "Main background gradient missing in CSS or HTML")

    def test_premium_header_style(self):
        """Rule: Institutional headers must have 4px letter-spacing."""
        with open(self.preview_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Look for the letter-spacing in the style block or inline
        # Normalize spaces
        content_clean = content.replace(" ", "").replace("\n", "").replace("\t", "")
        self.assertIn(
            "letter-spacing:4px",
            content_clean,
            "Institutional letter-spacing (4px) missing in headers",
        )

    def test_header_weight_enforcement(self):
        """Rule: Section headers must have font-weight: 900."""
        with open(self.preview_path, "r", encoding="utf-8") as f:
            content = f.read()
        content_clean = content.replace(" ", "").replace("\n", "").replace("\t", "")
        self.assertIn("font-weight:900", content_clean, "Section headers missing font-weight: 900")


if __name__ == "__main__":
    unittest.main()
