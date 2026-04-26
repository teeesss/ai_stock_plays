"""
test_table_density.py
=====================
TDD — RED phase. Tests that WILL FAIL until table-layout:fixed and ticker stacking are implemented.

Covers:
  1. table must have table-layout:fixed (the reason th widths were ignored)
  2. Ticker cell: compound tickers must render primary + stacked OTC (not side-by-side with /)
  3. ticker-sep '/' must NOT be used for compound tickers
  4. Company td must have max-width or overflow:hidden to prevent column blowout
  5. th widths must be present (already done)
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML_FILE = ROOT / "web" / "semi" / "index_template.html"


class TestTableLayoutFixed(unittest.TestCase):
    """table-layout:fixed is the ONLY way th widths are honoured by the browser."""

    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8") if HTML_FILE.exists() else ""

    def test_html_exists(self):
        self.assertTrue(HTML_FILE.exists())

    def test_table_layout_fixed_in_css(self):
        """table CSS rule must include table-layout:fixed."""
        self.assertIn(
            "table-layout",
            self.html,
            "FAIL: table CSS missing table-layout — th widths are completely ignored by browser",
        )
        self.assertIn(
            "fixed",
            (self.html.split("table-layout")[1][:20] if "table-layout" in self.html else ""),
            "FAIL: table-layout must be 'fixed'",
        )

    def test_company_td_has_max_width(self):
        """Company column must cap width so long names can't blow the layout."""
        # Either max-width on td.company or overflow is set
        self.assertTrue(
            "max-width" in self.html or "text-overflow: ellipsis" in self.html,
            "FAIL: no max-width constraint on Company column",
        )


class TestTickerStacking(unittest.TestCase):
    """Compound tickers (ASMPT / ASMPF) must stack vertically, not side-by-side."""

    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8") if HTML_FILE.exists() else ""

    def test_buildTickerHTML_uses_block_display_for_otc(self):
        """OTC ticker must render in a block/flex column so it stacks below primary."""
        # ticker-otc class must be display:block or flex column
        # We check that ticker-otc is NOT inline (no side-by-side slash)
        otc_css = re.search(r"\.ticker-otc\s*\{([^}]+)\}", self.html)
        self.assertIsNotNone(otc_css, "FAIL: .ticker-otc CSS class not found")
        css_body = otc_css.group(1)
        self.assertTrue(
            "block" in css_body or "flex" in css_body,
            f"FAIL: .ticker-otc must be display:block to stack below primary, got: {css_body}",
        )

    def test_ticker_sep_slash_not_used_between_tickers(self):
        """The inline '/' separator between primary and OTC must be removed."""
        self.assertNotIn(
            "ticker-sep",
            self.html,
            "FAIL: ticker-sep '/' still present — OTC renders side-by-side, not stacked",
        )

    def test_otc_label_present_in_ticker_builder(self):
        """buildTickerHTML must label the OTC ticker (e.g. 'OTC:' prefix or dimmed)."""
        # Check that OTC label or dimmed display is in buildTickerHTML region
        builder_match = re.search(
            r"function buildTickerHTML.*?^}", self.html, re.DOTALL | re.MULTILINE
        )
        self.assertIsNotNone(builder_match, "FAIL: buildTickerHTML not found")
        builder_src = builder_match.group(0)
        self.assertTrue(
            "ticker-otc" in builder_src,
            "FAIL: buildTickerHTML must use ticker-otc class for the OTC part",
        )
        # Must NOT have ticker-sep in builder (side-by-side slash)
        self.assertNotIn(
            "ticker-sep",
            builder_src,
            "FAIL: buildTickerHTML still uses ticker-sep — stacking not implemented",
        )


if __name__ == "__main__":
    print("=" * 60)
    print("Table Density TDD — RED PHASE (expect failures)")
    print("=" * 60)
    unittest.main(verbosity=2)
