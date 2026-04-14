"""
test_dashboard_filters.py
=========================
V1.0 — Tests for the cpo_plays.html passesFilters() logic fixes (2026-04-14).

Covers:
  1. P/E sentinel value (999 = no EPS data) — should be excluded ONLY when max filter is set
  2. OBB null-safe access — filters must only trigger when data exists
  3. Buzz count parsing as integer (not float)
  4. Duplicate function detection: cpo_plays.html must NOT define filterIntel() more than once
  5. passesFilters logic simulation in Python (mirrors JS logic)

These tests run without a browser — they validate the logic in isolation
and scan the HTML source for structural issues.
"""
import re
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML_FILE = ROOT / "cpo_plays.html"

# ---------------------------------------------------------------------------
# Helpers — mirror the JS passesFilters logic in Python
# ---------------------------------------------------------------------------
INF = float("inf")
NEG_INF = float("-inf")

def sfloat(val):
    """Mirror JS sfloat() — parse or return 0."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def passes_filters(entry, state):
    """
    Python mirror of the fixed JS passesFilters() function.
    entry keys: mcapB, pe26, pe27, obb (dict), buzz (dict with '7d'), alpha, rev_num
    state keys: minMcap, maxMcap, minPe26, maxPe26, minPe27, maxPe27,
                minInst, maxInst, minShort, maxShort, minAnalysts, maxAnalysts,
                minBuzz, maxBuzz, minAlpha, maxAlpha, minRev
    """
    # mcap
    if entry["mcapB"] < state.get("minMcap", NEG_INF): return False
    if entry["mcapB"] > state.get("maxMcap", INF): return False

    # P/E 26
    min_pe26 = state.get("minPe26", NEG_INF)
    max_pe26 = state.get("maxPe26", INF)
    pe26_active = min_pe26 > NEG_INF or max_pe26 < INF
    if pe26_active:
        has_pe26 = entry["pe26"] < 999
        if max_pe26 < INF and not has_pe26:
            return False  # max filter set, no data -> exclude
        if has_pe26 and (entry["pe26"] < min_pe26 or entry["pe26"] > max_pe26):
            return False

    # P/E 27
    min_pe27 = state.get("minPe27", NEG_INF)
    max_pe27 = state.get("maxPe27", INF)
    pe27_active = min_pe27 > NEG_INF or max_pe27 < INF
    if pe27_active:
        has_pe27 = entry["pe27"] < 999
        if max_pe27 < INF and not has_pe27:
            return False
        if has_pe27 and (entry["pe27"] < min_pe27 or entry["pe27"] > max_pe27):
            return False

    # OBB fields
    obb = entry.get("obb") or {}
    inst_pct = sfloat(obb.get("inst_ownership_pct"))
    short_pct = sfloat(obb.get("short_interest_pct"))
    analysts = sfloat(obb.get("analyst_count"))
    has_inst = obb.get("inst_ownership_pct") is not None and obb.get("inst_ownership_pct") != ""
    has_short = obb.get("short_interest_pct") is not None and obb.get("short_interest_pct") != ""
    has_analysts = obb.get("analyst_count") is not None and obb.get("analyst_count") != ""

    min_inst = state.get("minInst", NEG_INF)
    max_inst = state.get("maxInst", INF)
    if min_inst > NEG_INF or max_inst < INF:
        if not has_inst: return False
        if inst_pct < min_inst or inst_pct > max_inst: return False

    min_short = state.get("minShort", NEG_INF)
    max_short = state.get("maxShort", INF)
    if min_short > NEG_INF or max_short < INF:
        if not has_short: return False
        if short_pct < min_short or short_pct > max_short: return False

    min_analysts = state.get("minAnalysts", NEG_INF)
    max_analysts = state.get("maxAnalysts", INF)
    if min_analysts > NEG_INF or max_analysts < INF:
        if not has_analysts: return False
        if analysts < min_analysts or analysts > max_analysts: return False

    # Buzz (int parse)
    buzz_7d_raw = (entry.get("buzz") or {}).get("7d", "0")
    try:
        buzz_count = int(str(buzz_7d_raw))
    except (ValueError, TypeError):
        buzz_count = 0

    min_buzz = state.get("minBuzz", NEG_INF)
    max_buzz = state.get("maxBuzz", INF)
    if min_buzz > NEG_INF or max_buzz < INF:
        if buzz_count < min_buzz or buzz_count > max_buzz: return False

    return True


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

class TestPEFilterLogic(unittest.TestCase):
    """P/E sentinel (999 = no data) filtering logic."""

    def _entry(self, pe26=999, pe27=999):
        return {"mcapB": 10, "pe26": pe26, "pe27": pe27, "obb": {}, "buzz": {}, "rev_num": 0}

    def test_no_filter_active_passes_all(self):
        """With no P/E filter, all stocks (even no-data 999) should pass."""
        entry = self._entry(pe26=999, pe27=999)
        state = {}
        self.assertTrue(passes_filters(entry, state))

    def test_max_pe26_filter_excludes_no_data(self):
        """Setting maxPe26 should EXCLUDE stocks with no P/E data (999)."""
        entry = self._entry(pe26=999)
        state = {"maxPe26": 50}
        self.assertFalse(passes_filters(entry, state))

    def test_min_pe26_only_allows_no_data(self):
        """Setting ONLY minPe26 should NOT exclude stocks with no P/E data."""
        entry = self._entry(pe26=999)
        state = {"minPe26": 10}
        self.assertTrue(passes_filters(entry, state), "No-data stocks should pass min-only filter")

    def test_pe26_in_range_passes(self):
        """P/E 26 within the range should pass."""
        entry = self._entry(pe26=35)
        state = {"minPe26": 20, "maxPe26": 50}
        self.assertTrue(passes_filters(entry, state))

    def test_pe26_out_of_range_fails(self):
        """P/E 26 outside the range should fail."""
        entry = self._entry(pe26=80)
        state = {"minPe26": 20, "maxPe26": 50}
        self.assertFalse(passes_filters(entry, state))

    def test_max_pe27_excludes_no_data(self):
        """maxPe27 set should exclude stocks with no P/E 2027 data."""
        entry = self._entry(pe27=999)
        state = {"maxPe27": 60}
        self.assertFalse(passes_filters(entry, state))

    def test_pe27_in_range_passes(self):
        """P/E 27 in range should pass."""
        entry = self._entry(pe27=25)
        state = {"minPe27": 10, "maxPe27": 40}
        self.assertTrue(passes_filters(entry, state))

    def test_old_bug_regression(self):
        """
        REGRESSION: Old code did e.pe26 < state.minPe26 with NO check for 999.
        This means a stock with pe26=999 and minPe26=10 would FAIL (999 < 10 is False,
        999 > Infinity is False — it would pass). But set maxPe26=50:
        999 > 50 → old code FAILED the stock. Fixed code: no max set → pass through.
        With max set → exclude 999.
        """
        entry = self._entry(pe26=999)
        # Old bug: this would incorrectly fail (999 > 50)
        state = {"maxPe26": 50}
        result = passes_filters(entry, state)
        # New correct behavior: should EXCLUDE (no data, but max filter is active)
        self.assertFalse(result, "Max P/E filter should exclude no-data stocks")

        # Also test: min only should ALLOW no-data
        state_min_only = {"minPe26": 10}
        result_min = passes_filters(entry, state_min_only)
        self.assertTrue(result_min, "Min-only P/E filter should allow no-data stocks")


class TestOBBNullSafeFiltering(unittest.TestCase):
    """OBB filters must handle missing/null/empty data without crashing."""

    def _entry_no_obb(self):
        return {"mcapB": 5, "pe26": 999, "pe27": 999, "obb": None, "buzz": {}}

    def _entry_with_obb(self, **kwargs):
        return {"mcapB": 5, "pe26": 999, "pe27": 999, "obb": kwargs, "buzz": {}}

    def test_no_obb_data_with_inst_filter_excludes(self):
        """If inst filter is active but stock has no OBB data, it should be excluded."""
        entry = self._entry_no_obb()
        state = {"minInst": 50}
        self.assertFalse(passes_filters(entry, state))

    def test_no_obb_data_no_filter_passes(self):
        """If no OBB filter is active, stocks with no OBB data should still pass."""
        entry = self._entry_no_obb()
        state = {}
        self.assertTrue(passes_filters(entry, state))

    def test_inst_in_range_passes(self):
        """Institutional ownership within range should pass."""
        entry = self._entry_with_obb(inst_ownership_pct=75.0)
        state = {"minInst": 50, "maxInst": 100}
        self.assertTrue(passes_filters(entry, state))

    def test_inst_out_of_range_fails(self):
        """Institutional ownership outside range should fail."""
        entry = self._entry_with_obb(inst_ownership_pct=30.0)
        state = {"minInst": 50}
        self.assertFalse(passes_filters(entry, state))

    def test_short_interest_filter(self):
        """Short interest filter should work correctly."""
        entry = self._entry_with_obb(short_interest_pct=12.5)
        self.assertTrue(passes_filters(entry, {"maxShort": 15}))
        self.assertFalse(passes_filters(entry, {"maxShort": 10}))

    def test_analyst_count_filter(self):
        """Analyst count filter should work correctly."""
        entry = self._entry_with_obb(analyst_count=10)
        self.assertTrue(passes_filters(entry, {"minAnalysts": 5}))
        self.assertFalse(passes_filters(entry, {"minAnalysts": 15}))

    def test_no_obb_short_filter_excludes(self):
        """Active short filter with missing data → exclude."""
        entry = self._entry_no_obb()
        state = {"minShort": 5}
        self.assertFalse(passes_filters(entry, state))

    def test_empty_string_obb_treated_as_no_data(self):
        """OBB fields set to empty string should be treated as no data."""
        entry = self._entry_with_obb(inst_ownership_pct="", short_interest_pct="", analyst_count="")
        state = {"minInst": 10}
        self.assertFalse(passes_filters(entry, state), "Empty string OBB should be treated as no data")


class TestBuzzFilterParsing(unittest.TestCase):
    """Buzz 7d count must be parsed as integer, not float."""

    def _entry(self, buzz_7d):
        return {"mcapB": 5, "pe26": 999, "pe27": 999, "obb": {}, "buzz": {"7d": buzz_7d}}

    def test_buzz_integer_string_in_range(self):
        """Buzz count as string integer in range should pass."""
        entry = self._entry("15")
        state = {"minBuzz": 10, "maxBuzz": 20}
        self.assertTrue(passes_filters(entry, state))

    def test_buzz_integer_out_of_range(self):
        """Buzz count below minBuzz should fail."""
        entry = self._entry("3")
        state = {"minBuzz": 5}
        self.assertFalse(passes_filters(entry, state))

    def test_buzz_zero_no_filter(self):
        """No buzz filter → stock with 0 buzz passes."""
        entry = self._entry(0)
        state = {}
        self.assertTrue(passes_filters(entry, state))

    def test_buzz_none_treated_as_zero(self):
        """Missing buzz data treated as 0."""
        entry = {"mcapB": 5, "pe26": 999, "pe27": 999, "obb": {}, "buzz": None}
        state = {"minBuzz": 5}
        self.assertFalse(passes_filters(entry, state))

    def test_buzz_integer_value(self):
        """Buzz count as raw int should work."""
        entry = self._entry(42)
        state = {"minBuzz": 40, "maxBuzz": 50}
        self.assertTrue(passes_filters(entry, state))


class TestHTMLStructuralIntegrity(unittest.TestCase):
    """Scan the actual cpo_plays.html for structural bugs."""

    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8") if HTML_FILE.exists() else ""

    def test_html_file_exists(self):
        """The dashboard HTML file must exist."""
        self.assertTrue(HTML_FILE.exists(), f"{HTML_FILE} not found")

    def test_no_duplicate_filterIntel_definition(self):
        """
        REGRESSION: filterIntel() was defined twice (lines 620 & 682).
        The second definition silently overrode the first (correct) one.
        Must have exactly ONE definition.
        """
        matches = re.findall(r'\bfunction filterIntel\s*\(', self.html)
        self.assertEqual(len(matches), 1,
            f"Expected 1 filterIntel() definition, found {len(matches)}. "
            "Duplicate definitions cause silent override bugs.")

    def test_no_duplicate_openIntelModal_definition(self):
        """openIntelModal() must be defined exactly once."""
        matches = re.findall(r'\bfunction openIntelModal\s*\(', self.html)
        self.assertEqual(len(matches), 1,
            f"Expected 1 openIntelModal() definition, found {len(matches)}.")

    def test_no_duplicate_renderBuzz_definition(self):
        """renderBuzz() must be defined exactly once."""
        matches = re.findall(r'\bfunction renderBuzz\s*\(', self.html)
        self.assertEqual(len(matches), 1,
            f"Expected 1 renderBuzz() definition, found {len(matches)}.")

    def test_passesFilters_uses_null_safe_obb_access(self):
        """
        passesFilters() must use null-safe OBB access (e.obb?.inst_ownership_pct).
        Old bad code: sfloat(e.obb.inst_ownership_pct) — crashes if obb is null.
        """
        # Check that the new code uses hasInst/hasShort/hasAnalysts pattern
        self.assertIn("hasInst", self.html,
            "passesFilters must define hasInst for null-safe OBB access")
        self.assertIn("hasShort", self.html,
            "passesFilters must define hasShort for null-safe OBB access")
        self.assertIn("hasAnalysts", self.html,
            "passesFilters must define hasAnalysts for null-safe OBB access")

    def test_buzz_uses_parseInt_not_sfloat(self):
        """Buzz count must use parseInt() for buzz 7d, not sfloat()."""
        # Find the buzz filter section
        buzz_section = re.search(
            r'buzzCount.*?minBuzz.*?maxBuzz',
            self.html,
            re.DOTALL
        )
        self.assertIsNotNone(buzz_section, "Could not find buzz filter section")
        self.assertIn("parseInt", buzz_section.group(0),
            "Buzz filter must use parseInt(), not sfloat()")

    def test_pe_filter_uses_sentinel_logic(self):
        """P/E filter must reference 999 sentinel for no-data detection."""
        self.assertIn("999", self.html,
            "P/E filter logic must reference 999 sentinel for no-EPS stocks")
        self.assertIn("pe26Active", self.html,
            "P/E 26 filter must use pe26Active flag")

    def test_passes_filters_defined(self):
        """passesFilters function must be present in HTML."""
        self.assertIn("function passesFilters", self.html,
            "passesFilters() function must be defined in cpo_plays.html")


if __name__ == "__main__":
    print("=" * 60)
    print("Dashboard Filter QA — V1.0")
    print("Tests passesFilters() fix for P/E, OBB, Buzz, and duplicate functions")
    print("=" * 60)
    unittest.main(verbosity=2)
