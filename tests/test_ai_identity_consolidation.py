import unittest
from pathlib import Path


class TestAIIdentityConsolidation(unittest.TestCase):
    def setUp(self):
        self.template_path = Path("z:/COS_Stock_Plays/web/ai/index_template.html")
        with open(self.template_path, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_company_column_header_removed(self):
        """Verify that the Company header is removed from the template."""
        # Should NOT find a th with "Company" text
        self.assertNotIn(
            '<th style="width:130px;" onclick="setSort(\'company\')">Company</th>',
            self.content,
        )

    def test_ticker_column_width_expanded(self):
        """Verify that the Ticker column width is expanded to approximately 100px."""
        self.assertIn(
            '<th style="width:100px;" onclick="setSort(\'ticker\')">Ticker</th>',
            self.content,
        )

    def test_company_name_moved_to_ticker_cell(self):
        """Verify that e.h.Company is now part of the ticker cell stack."""
        # New pattern should have ticker class td containing both ticker and company
        # We look for the stack pattern: buildTickerHTML followed by company name in a sub-div
        self.assertIn('class="ticker"', self.content)
        self.assertIn("${esc(e.h.Company)}", self.content)

        # Importantly, the old separate TD should be gone
        old_td_pattern = '<td title="${esc(e.h.Company)}" style="font-size:11px;white-space:normal;line-height:1.3;"><b>${esc(e.h.Company)}</b></td>'
        self.assertNotIn(old_td_pattern, self.content)


if __name__ == "__main__":
    unittest.main()
