"""
GIGACPO Data Standardizer
Handles normalization of tickers, exchanges, and categories to ensure consistency.
Fixes case-sensitivity and data-mismatch issues.
"""

class DataStandardizer:
    @staticmethod
    def normalize_bucket(bucket_name):
        """Standardizes bucket names to proper casing (PascalCase)."""
        if not bucket_name: return "Uncategorized"
        # Map specific common mis-casings
        mapping = {
            "AI WATCHLIST": "AI Watchlist",
            "SEMICONDUCTORS": "Semiconductors",
            "PRIVATE": "Private",
            "CHIPS": "Semiconductors"
        }
        return mapping.get(bucket_name.upper(), bucket_name)

    @staticmethod
    def normalize_exchange(exchange):
        """Standardizes exchange codes to meaningful abbreviations."""
        if not exchange: return "US"
        m = {
            "NasdaqGS": "NASDAQ",
            "NasdaqCM": "NASDAQ",
            "NasdaqGM": "NASDAQ",
            "NYSE": "NYSE",
            "NYSE American": "NYSE-A",
            "OTC Markets": "OTC",
            "PNK": "OTC",
            "ASX": "ASX",
            "LSE": "LSE",
            "FRA": "FRA"
        }
        return m.get(exchange, exchange)

    @staticmethod
    def clean_ticker(ticker):
        """Collapses fragments like '$ N V D A' and strips leading $."""
        if not ticker: return ""
        cleaned = ticker.replace(" ", "").replace("$", "").upper()
        return cleaned

    @staticmethod
    def format_mcap(mcap_raw):
        """Converts raw market cap to Billions."""
        if not mcap_raw: return 0
        return mcap_raw / 1e9
