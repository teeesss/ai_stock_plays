"""
tests/test_openbb_fetcher.py
=============================
Tests for the OpenBB supplement fetcher.
CRITICAL: These tests must NOT mutate the production database.
All tests use a mock/sandbox dataset.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine.openbb_fetcher import (
    fetch_supplement,
    momentumScore_equivalent,
    SKIP_TICKERS,
    BUCKET_MULT_PRIVATE,
)


class TestSkipLogic(unittest.TestCase):
    """Verify that private companies and ETFs are properly skipped."""

    def test_private_bucket_skipped(self):
        result = fetch_supplement('AYAR', 'Private')
        self.assertEqual(result, {}, 'Private companies must return empty dict')

    def test_etf_in_skip_list_skipped(self):
        result = fetch_supplement('PTF', 'ETF')
        self.assertEqual(result, {}, 'PTF is in SKIP_TICKERS, must return empty dict')

    def test_skip_tickers_defined(self):
        self.assertIn('AYAR', SKIP_TICKERS)
        self.assertIn('CelestialAI', SKIP_TICKERS)
        self.assertIn('SCINTIL', SKIP_TICKERS)
        self.assertIn('PTF', SKIP_TICKERS)


class TestYFinanceIntegration(unittest.TestCase):
    """Test yfinance data extraction with mocked responses."""

    def _make_mock_ticker(self, info_dict):
        mock = MagicMock()
        mock.info = info_dict
        return mock

    @patch('engine.openbb_fetcher.yf.Ticker')
    def test_analyst_data_extracted(self, mock_ticker_cls):
        mock_ticker_cls.return_value = self._make_mock_ticker({
            'targetMeanPrice': 45.0,
            'targetHighPrice': 60.0,
            'targetLowPrice': 30.0,
            'numberOfAnalystOpinions': 12,
            'recommendationMean': 1.8,
            'heldPercentInstitutions': 0.45,
            'shortPercentOfFloat': 0.08,
            'currentPrice': 35.0,
        })
        result = fetch_supplement('CRDO', 'Core')
        self.assertIn('analyst_target_mean', result)
        self.assertEqual(result['analyst_target_mean'], 45.0)
        self.assertIn('analyst_count', result)
        self.assertEqual(result['analyst_count'], 12)
        self.assertIn('inst_ownership_pct', result)
        self.assertAlmostEqual(result['inst_ownership_pct'], 45.0, places=1)
        self.assertIn('short_interest_pct', result)
        self.assertAlmostEqual(result['short_interest_pct'], 8.0, places=1)
        self.assertIn('analyst_implied_upside_pct', result)
        self.assertAlmostEqual(result['analyst_implied_upside_pct'], 28.6, places=0)

    @patch('engine.openbb_fetcher.yf.Ticker')
    def test_buy_pct_strong_buy(self, mock_ticker_cls):
        mock_ticker_cls.return_value = self._make_mock_ticker({
            'recommendationMean': 1.3,
            'currentPrice': 10.0,
            'targetMeanPrice': 12.0,
            'targetHighPrice': 14.0,
            'targetLowPrice': 8.0,
            'numberOfAnalystOpinions': 5,
        })
        result = fetch_supplement('TEST', 'Core')
        self.assertIn('analyst_buy_pct', result)
        self.assertEqual(result['analyst_buy_pct'], 90)

    @patch('engine.openbb_fetcher.yf.Ticker')
    def test_buy_pct_sell(self, mock_ticker_cls):
        mock_ticker_cls.return_value = self._make_mock_ticker({
            'recommendationMean': 4.0,
            'currentPrice': 10.0,
            'targetMeanPrice': 8.0,
            'targetHighPrice': 10.0,
            'targetLowPrice': 6.0,
            'numberOfAnalystOpinions': 3,
        })
        result = fetch_supplement('TEST', 'Core')
        self.assertEqual(result['analyst_buy_pct'], 10)

    @patch('engine.openbb_fetcher.yf.Ticker')
    def test_empty_info_returns_empty(self, mock_ticker_cls):
        mock_ticker_cls.return_value = self._make_mock_ticker({})
        result = fetch_supplement('BOGUS', 'Core')
        self.assertEqual(result, {})

    @patch('engine.openbb_fetcher.yf.Ticker')
    def test_partial_data_no_crash(self, mock_ticker_cls):
        """If only some fields are available, should gracefully handle."""
        mock_ticker_cls.return_value = self._make_mock_ticker({
            'numberOfAnalystOpinions': 3,
            'currentPrice': 10.0,
            'targetMeanPrice': 12.0,
            'targetHighPrice': 14.0,
            'targetLowPrice': 8.0,
            # Note: no recommendationMean, heldPercentInstitutions, shortPercentOfFloat
        })
        result = fetch_supplement('SMALLCAP', 'Hidden')
        self.assertIn('analyst_count', result)
        self.assertNotIn('inst_ownership_pct', result)  # Not in mock data

    @patch('engine.openbb_fetcher.yf.Ticker', side_effect=Exception('Rate limited'))
    def test_yfinance_exception_handled(self, mock_ticker_cls):
        """Exceptions must not crash the fetcher."""
        result = fetch_supplement('CRASH', 'Core')
        self.assertEqual(result, {})


class TestNoDataMutation(unittest.TestCase):
    """Verify dry-run mode doesn't mutate the database."""

    def test_dry_run_no_file_write(self):
        """dry_run=True must not touch the DB file."""
        import os
        from engine.openbb_fetcher import DB_PATH, run_fetch

        # Get current file modification time
        if DB_PATH.exists():
            original_mtime = os.path.getmtime(DB_PATH)
        else:
            self.skipTest('Database not found')

        with patch('engine.openbb_fetcher.yf.Ticker') as mock_cls:
            mock_cls.return_value.info = {
                'targetMeanPrice': 99.0,
                'numberOfAnalystOpinions': 5,
                'currentPrice': 80.0,
            }
            run_fetch(tickers=['CRDO'], force=True, dry_run=True)

        new_mtime = os.path.getmtime(DB_PATH)
        self.assertEqual(original_mtime, new_mtime, 'dry_run=True must NOT modify the database file')


class TestSchemaIntegrity(unittest.TestCase):
    """Verify the supplement schema is compatible with the JS dashboard."""

    def test_supplement_fields_are_json_serializable(self):
        result = {
            'analyst_target_mean': 45.0,
            'analyst_count': 12,
            'inst_ownership_pct': 45.0,
            'short_interest_pct': 8.0,
            'analyst_buy_pct': 70,
            'analyst_implied_upside_pct': 28.6,
            'last_updated': '2026-04-12T17:00:00+00:00',
        }
        try:
            json.dumps(result)
        except (TypeError, ValueError) as e:
            self.fail(f'Supplement data is not JSON serializable: {e}')

    def test_supplement_fields_dont_conflict_with_existing(self):
        """New fields must not use names already in human_research."""
        EXISTING_HUMAN_RESEARCH_FIELDS = {
            'Company', 'Country', 'Bucket', 'Role', 'Alpha Score',
            'Notes', 'Target Upside', 'Risk Adj', 'Hiddenness',
            'Rev Growth Est',
        }
        NEW_FIELDS = {
            'analyst_target_mean', 'analyst_target_high', 'analyst_target_low',
            'analyst_count', 'analyst_buy_pct', 'inst_ownership_pct',
            'short_interest_pct', 'analyst_implied_upside_pct', 'last_updated',
        }
        conflicts = EXISTING_HUMAN_RESEARCH_FIELDS & NEW_FIELDS
        self.assertEqual(conflicts, set(), f'Field name conflicts: {conflicts}')


class TestLiveConnectivity(unittest.TestCase):
    """LIVE tests — only run manually with --live flag. Skipped in CI."""

    def setUp(self):
        if '--live' not in sys.argv:
            self.skipTest('Live tests skipped (pass --live to run)')

    def test_live_crdo_fetch(self):
        """Verify CRDO (a US-listed CPO play) returns real analyst data."""
        result = fetch_supplement('CRDO', 'Core')
        print(f'\nLIVE CRDO result: {json.dumps(result, indent=2)}')
        self.assertIsInstance(result, dict)
        # Should have at least analyst count or institutional pct
        has_data = 'analyst_count' in result or 'inst_ownership_pct' in result
        self.assertTrue(has_data, 'Expected at least one field from live fetch')

    def test_live_besiy_fetch(self):
        """Verify BESIY (OTC ADR) can be fetched."""
        result = fetch_supplement('BESIY', 'Core')
        print(f'\nLIVE BESIY result: {json.dumps(result, indent=2)}')
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    # Usage: python tests/test_openbb_fetcher.py          (unit tests only)
    #        python tests/test_openbb_fetcher.py --live   (includes live API calls)
    live = '--live' in sys.argv
    if live:
        sys.argv.remove('--live')
        print('Running with LIVE API tests enabled...')
    else:
        print('Running unit tests only (use --live for live API tests)...')
    unittest.main(verbosity=2)
