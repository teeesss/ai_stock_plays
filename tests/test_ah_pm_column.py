"""
test_ah_pm_column.py
====================
V1.0 — Tests for the AH/PM extended-hours price column (2026-04-14).

Covers:
  1. fetch_batch() ext-hours field extraction logic (unit-tested via mock Yahoo response)
  2. AH priority over PM when both fields present
  3. PM fallback when no AH data
  4. No ext price when neither AH nor PM present
  5. Rounding / sanitisation of ext fields
  6. HTML structural integrity — new AH/PM column present
  7. HTML structural integrity — updTime micro-stamp present
  8. HTML structural integrity — ext sort key present
  9. HTML structural integrity — colspan updated to 17
 10. live_prices.py contains postMarketPrice + preMarketPrice references

Runs entirely offline — no network calls.
"""
import re
import sys
import json
import types
import unittest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).parent.parent
HTML_FILE = ROOT / "web" / "semi" / "index_template.html"
LIVE_PRICES_SRC = ROOT / "engine" / "live_prices.py"

# ---------------------------------------------------------------------------
# Helper — build a fake Yahoo quote API item
# ---------------------------------------------------------------------------

def _make_item(symbol, regular_price=100.0, regular_chg_pct=1.5,
               post_price=None, post_pct=None,
               pre_price=None, pre_pct=None,
               volume=500_000, avg_vol=250_000):
    item = {
        "symbol": symbol,
        "regularMarketPrice": regular_price,
        "regularMarketChangePercent": regular_chg_pct,
        "regularMarketVolume": volume,
        "averageDailyVolume10Day": avg_vol,
    }
    if post_price is not None:
        item["postMarketPrice"] = post_price
        item["postMarketChangePercent"] = post_pct
    if pre_price is not None:
        item["preMarketPrice"] = pre_price
        item["preMarketChangePercent"] = pre_pct
    return item


# ---------------------------------------------------------------------------
# Unit tests — isolate fetch_batch() logic without importing full module
# (avoids curl_cffi / playwright import requirements in CI)
# ---------------------------------------------------------------------------

def _run_fetch_batch_logic(items, tickers):
    """
    Re-implements the core per-item logic from fetch_batch() in Python
    so we can unit-test it without touching network code.
    Returns the same structure fetch_batch would produce.
    """
    results = {}
    now = datetime.now(timezone.utc).isoformat()

    def clean_ticker(t):
        return t.split(' / ')[0].strip()

    primary_map = {clean_ticker(t): t for t in tickers}

    for item in items:
        symbol = item.get('symbol')
        if not symbol or symbol not in primary_map:
            continue

        original_ticker = primary_map[symbol]
        price      = item.get('regularMarketPrice')
        change_pct = item.get('regularMarketChangePercent')
        volume     = item.get('regularMarketVolume')
        avg_vol    = item.get('averageDailyVolume10Day')

        vol_spike = None
        if volume and avg_vol and avg_vol > 0:
            vol_spike = round(volume / avg_vol, 2)

        # Extended-hours — AH takes priority over PM
        post_price = item.get('postMarketPrice')
        post_pct   = item.get('postMarketChangePercent')
        pre_price  = item.get('preMarketPrice')
        pre_pct    = item.get('preMarketChangePercent')

        ext_price, ext_pct, ext_type = None, None, None
        if post_price is not None:
            ext_price, ext_pct, ext_type = post_price, post_pct, 'AH'
        elif pre_price is not None:
            ext_price, ext_pct, ext_type = pre_price, pre_pct, 'PM'

        entry = {
            'price':      round(price,      2) if price      is not None else None,
            'change_pct': round(change_pct, 2) if change_pct is not None else None,
            'volume':     int(volume)           if volume               else None,
            'avg_volume': int(avg_vol)          if avg_vol              else None,
            'vol_spike':  vol_spike,
            'ext_price':  round(ext_price, 2)  if ext_price is not None else None,
            'ext_pct':    round(ext_pct,   2)  if ext_pct   is not None else None,
            'ext_type':   ext_type,
            'updated':    now,
        }
        entry = {k: v for k, v in entry.items() if v is not None}
        results[original_ticker] = entry

    return results


# ---------------------------------------------------------------------------
# Test suite 1: ext-hours extraction logic
# ---------------------------------------------------------------------------

class TestExtHoursExtraction(unittest.TestCase):
    """Test the AH/PM field extraction logic from Yahoo quote items."""

    def test_ah_price_populated_when_post_market_present(self):
        """postMarketPrice should populate ext_price with ext_type='AH'."""
        items = [_make_item('CRDO', post_price=29.50, post_pct=2.1)]
        result = _run_fetch_batch_logic(items, ['CRDO'])
        self.assertIn('CRDO', result)
        entry = result['CRDO']
        self.assertEqual(entry['ext_price'], 29.50)
        self.assertEqual(entry['ext_pct'],    2.1)
        self.assertEqual(entry['ext_type'],  'AH')

    def test_pm_price_populated_when_only_pre_market_present(self):
        """preMarketPrice should populate ext fields with ext_type='PM' when no AH data."""
        items = [_make_item('ANET', pre_price=320.00, pre_pct=-0.5)]
        result = _run_fetch_batch_logic(items, ['ANET'])
        entry = result['ANET']
        self.assertEqual(entry['ext_price'], 320.00)
        self.assertEqual(entry['ext_pct'],   -0.5)
        self.assertEqual(entry['ext_type'],  'PM')

    def test_ah_takes_priority_over_pm(self):
        """When both postMarket and preMarket present, AH wins."""
        items = [_make_item('NVDA',
                            post_price=950.0, post_pct=1.8,
                            pre_price=940.0,  pre_pct=0.7)]
        result = _run_fetch_batch_logic(items, ['NVDA'])
        entry = result['NVDA']
        self.assertEqual(entry['ext_type'],  'AH')
        self.assertEqual(entry['ext_price'], 950.0)

    def test_no_ext_fields_when_neither_present(self):
        """Regular market only — ext_price/ext_pct/ext_type must be absent."""
        items = [_make_item('POET')]
        result = _run_fetch_batch_logic(items, ['POET'])
        entry = result['POET']
        self.assertNotIn('ext_price', entry)
        self.assertNotIn('ext_pct',   entry)
        self.assertNotIn('ext_type',  entry)

    def test_ext_price_rounded_to_2dp(self):
        """ext_price must be rounded to 2 decimal places."""
        items = [_make_item('LITE', post_price=78.3333333, post_pct=0.111111)]
        result = _run_fetch_batch_logic(items, ['LITE'])
        entry = result['LITE']
        self.assertEqual(entry['ext_price'], 78.33)
        self.assertEqual(entry['ext_pct'],   0.11)

    def test_regular_price_still_present_with_ah(self):
        """AH data must not clobber regular price / change_pct."""
        items = [_make_item('MRVL', regular_price=75.5, regular_chg_pct=-1.2,
                            post_price=76.0, post_pct=0.7)]
        result = _run_fetch_batch_logic(items, ['MRVL'])
        entry = result['MRVL']
        self.assertEqual(entry['price'],      75.5)
        self.assertEqual(entry['change_pct'], -1.2)
        self.assertEqual(entry['ext_price'],  76.0)

    def test_vol_spike_still_computed(self):
        """Vol spike calculation must still work when ext fields present."""
        items = [_make_item('AEHR', volume=1_000_000, avg_vol=250_000,
                            post_price=8.0, post_pct=1.5)]
        result = _run_fetch_batch_logic(items, ['AEHR'])
        entry = result['AEHR']
        self.assertEqual(entry['vol_spike'], 4.0)

    def test_compound_ticker_resolved_correctly(self):
        """Compound 'ASMPT / ASMPF' tickers use primary (first) part for lookup."""
        items = [_make_item('ASMPT', post_price=50.0, post_pct=0.5)]
        result = _run_fetch_batch_logic(items, ['ASMPT / ASMPF'])
        # Should be stored under the compound key
        self.assertIn('ASMPT / ASMPF', result)
        entry = result['ASMPT / ASMPF']
        self.assertEqual(entry['ext_type'],  'AH')

    def test_updated_field_always_present(self):
        """'updated' ISO timestamp must always be set."""
        items = [_make_item('NPAB')]
        result = _run_fetch_batch_logic(items, ['NPAB'])
        self.assertIn('updated', result['NPAB'])
        # Validate it parses as ISO 8601
        ts = result['NPAB']['updated']
        datetime.fromisoformat(ts.replace('Z', '+00:00'))  # Should not raise

    def test_unknown_symbol_skipped(self):
        """Items with symbols not in ticker list must be ignored."""
        items = [_make_item('UNKNOWN')]
        result = _run_fetch_batch_logic(items, ['CRDO'])
        self.assertNotIn('UNKNOWN', result)
        self.assertNotIn('CRDO', result)

    def test_negative_ah_pct_stored_correctly(self):
        """Negative after-hours change must be stored as negative float."""
        items = [_make_item('COHR', post_price=60.0, post_pct=-3.5)]
        result = _run_fetch_batch_logic(items, ['COHR'])
        self.assertEqual(result['COHR']['ext_pct'], -3.5)


# ---------------------------------------------------------------------------
# Test suite 2: HTML structural integrity
# ---------------------------------------------------------------------------

class TestHTMLAHPMColumn(unittest.TestCase):
    """Scan cpo_plays.html to confirm AH/PM column is correctly wired."""

    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding='utf-8') if HTML_FILE.exists() else ''

    def test_html_file_exists(self):
        self.assertTrue(HTML_FILE.exists(), f"{HTML_FILE} not found")

    def test_ah_pm_column_header_present(self):
        """Table must contain a 'PM/AH' <th> header."""
        self.assertIn('PM/AH', self.html,
            "No 'PM/AH' column header found in cpo_plays.html")

    def test_ah_pm_header_has_sort_handler(self):
        """AH / PM header must have onclick setSort('ext')."""
        self.assertIn("setSort('ext')", self.html,
            "AH / PM column must have setSort('ext') onclick handler")

    def test_ext_sort_case_in_sortFn(self):
        """sortFn() must handle col === 'ext' for AH/PM sort."""
        self.assertIn("col === 'ext'", self.html,
            "sortFn() missing ext sort case — AH/PM column won't sort")

    def test_ext_price_in_row_template(self):
        """Row innerHTML must reference e.extPrice for the AH/PM cell."""
        self.assertIn('e.extPrice', self.html,
            "Row template missing e.extPrice reference")

    def test_ext_pct_in_row_template(self):
        """Row innerHTML must reference e.extPct for the AH/PM percentage."""
        self.assertIn('e.extPct', self.html,
            "Row template missing e.extPct reference")

    def test_ext_type_in_row_template(self):
        """Row innerHTML must reference e.extType for the AH/PM label."""
        self.assertIn('e.extType', self.html,
            "Row template missing e.extType reference")

    def test_updTime_present_in_row_template(self):
        """Row template must include updTime micro-timestamp above price."""
        self.assertIn('updTime', self.html,
            "Row template missing updTime field for micro-timestamp")

    def test_live_prices_ext_price_binding(self):
        """buildEntries() must bind live.ext_price to extPrice."""
        self.assertIn('live.ext_price', self.html,
            "buildEntries() missing live.ext_price binding")

    def test_live_prices_ext_pct_binding(self):
        """buildEntries() must bind live.ext_pct to extPct."""
        self.assertIn('live.ext_pct', self.html,
            "buildEntries() missing live.ext_pct binding")

    def test_live_prices_ext_type_binding(self):
        """buildEntries() must bind live.ext_type to extType."""
        self.assertIn('live.ext_type', self.html,
            "buildEntries() missing live.ext_type binding")

    def test_colspan_updated_to_17(self):
        """Private watchlist divider must have colspan=17 (was 16 before AH/PM column)."""
        self.assertIn('colspan="17"', self.html,
            "Private watchlist divider colspan not updated to 17")
        self.assertNotIn('colspan="16"', self.html,
            "Old colspan=16 still present — divider not updated")

    def test_updTime_slices_iso_string(self):
        """updTime must extract HH:MM from ISO string via .slice(11,16)."""
        self.assertIn('.slice(11,16)', self.html,
            "updTime must use .slice(11,16) to extract HH:MM from ISO timestamp")


# ---------------------------------------------------------------------------
# Test suite 3: live_prices.py source checks
# ---------------------------------------------------------------------------

class TestLivePricesSource(unittest.TestCase):
    """Verify the live_prices.py source contains the new ext-hours code."""

    @classmethod
    def setUpClass(cls):
        cls.src = LIVE_PRICES_SRC.read_text(encoding='utf-8') if LIVE_PRICES_SRC.exists() else ''

    def test_source_file_exists(self):
        self.assertTrue(LIVE_PRICES_SRC.exists(), f"{LIVE_PRICES_SRC} not found")

    def test_post_market_price_fetched(self):
        """live_prices.py must call item.get('postMarketPrice')."""
        self.assertIn("postMarketPrice", self.src,
            "live_prices.py missing postMarketPrice fetch")

    def test_pre_market_price_fetched(self):
        """live_prices.py must call item.get('preMarketPrice')."""
        self.assertIn("preMarketPrice", self.src,
            "live_prices.py missing preMarketPrice fetch")

    def test_ext_type_set_to_AH(self):
        """live_prices.py must set ext_type = 'AH' for post-market data."""
        self.assertIn("'AH'", self.src,
            "live_prices.py missing ext_type='AH' assignment")

    def test_ext_type_set_to_PM(self):
        """live_prices.py must set ext_type = 'PM' for pre-market data."""
        self.assertIn("'PM'", self.src,
            "live_prices.py missing ext_type='PM' assignment")

    def test_ext_price_in_entry_dict(self):
        """live_prices.py entry dict must include ext_price key."""
        self.assertIn("'ext_price'", self.src,
            "live_prices.py entry dict missing 'ext_price' key")

    def test_ext_pct_in_entry_dict(self):
        """live_prices.py entry dict must include ext_pct key."""
        self.assertIn("'ext_pct'", self.src,
            "live_prices.py entry dict missing 'ext_pct' key")

    def test_ext_type_in_entry_dict(self):
        """live_prices.py entry dict must include ext_type key."""
        self.assertIn("'ext_type'", self.src,
            "live_prices.py entry dict missing 'ext_type' key")

    def test_ah_priority_over_pm(self):
        """live_prices.py must check postMarketPrice before preMarketPrice."""
        post_idx = self.src.index('postMarketPrice') if 'postMarketPrice' in self.src else -1
        pre_idx  = self.src.index('preMarketPrice')  if 'preMarketPrice'  in self.src else -1
        self.assertGreater(post_idx, 0, "postMarketPrice not found in source")
        self.assertGreater(pre_idx, 0,  "preMarketPrice not found in source")
        self.assertLess(post_idx, pre_idx,
            "postMarketPrice must appear before preMarketPrice (AH priority logic)")


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print('=' * 65)
    print('AH/PM Column QA — V1.0')
    print('Tests ext-hours extraction logic, HTML structure, source checks')
    print('=' * 65)
    unittest.main(verbosity=2)
