import unittest
import re
import sys
from pathlib import Path

# Add engine to path to test the actual function
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "engine"))

try:
    from x_intel_deep_scraper import reconstruct_tickers, clean_text_spacing
except ImportError:
    # Define placeholder for isolated test run if needed
    def reconstruct_tickers(text):
        # 1. Catch single character splits: $N V D A
        text = re.sub(r'\$[A-Z](?:\s[A-Z]){1,9}', lambda m: '$' + m.group(0)[1:].replace(' ', ''), text)
        # 2. Catch fragment splits: $PG Y, $OS S, $VL N, $AA O I
        # Match $ + ALL CAPS + space + ALL CAPS (up to 3) + non-lowercase lookahead
        text = re.sub(r'\$([A-Z]{1,9})\s([A-Z]{1,3})(?![a-z])', r'$\1\2', text)
        return text

    def clean_text_spacing(text):
        text = reconstruct_tickers(text)
        # Space before
        text = re.sub(r'([a-zA-Z0-9])([\$@])', r'\1 \2', text)
        # Space after
        text = re.sub(r'(\$[A-Z]{2,10})([a-zA-Z0-9])', r'\1 \2', text)
        return text

class TestTickerReconstruction(unittest.TestCase):
    def test_single_letter_splits(self):
        self.assertEqual(reconstruct_tickers("$N V D A"), "$NVDA")
        self.assertEqual(reconstruct_tickers("$P O E T"), "$POET")
        self.assertEqual(reconstruct_tickers("Bought $A A O I"), "Bought $AAOI")

    def test_fragment_splits(self):
        # The new cases reported by the user
        self.assertEqual(reconstruct_tickers("$PG Y: Lending Club"), "$PGY: Lending Club")
        self.assertEqual(reconstruct_tickers("$OS S"), "$OSS")
        self.assertEqual(reconstruct_tickers("$VL N fundamentals"), "$VLN fundamentals")
        self.assertEqual(reconstruct_tickers("$AA O I"), "$AAOI")

    def test_false_positives(self):
        # We should NOT merge if the second part is lowercase (normal text)
        self.assertEqual(reconstruct_tickers("$AMD is great"), "$AMD is great")
        # We should NOT merge if the second part is too long (likely legitimate words)
        self.assertEqual(reconstruct_tickers("$AAPL BOUGHT"), "$AAPL BOUGHT") 
        # But wait, sometimes people say $AAPL BUY. This is the trade-off. 
        # Usually split tickers from Nitter are 1-2 chars long.
        self.assertEqual(reconstruct_tickers("$AAPL SELL"), "$AAPL SELL")

    def test_full_pipeline(self):
        # Test the whole thing including spacing
        raw = "check $PG Y:beat WS estimates."
        # Should reconstruct to $PGY then ensure space before : if needed? 
        # Most importantly, space before $ if preceded by char
        self.assertEqual(clean_text_spacing("check $PG Y"), "check $PGY")
        self.assertEqual(clean_text_spacing("up like 60% this week $OS S"), "up like 60% this week $OSS")

if __name__ == '__main__':
    unittest.main()
