import unittest
import sys
from pathlib import Path

# Add engine to path
sys.path.append(str(Path(__file__).parent.parent / "engine"))
from ultimate_repair import ultimate_reconstruct

class TestTickerRepair(unittest.TestCase):
    def test_split_tickers(self):
        self.assertEqual(ultimate_reconstruct("$PG Y"), "$PGY")
        self.assertEqual(ultimate_reconstruct("$OS S"), "$OSS")
        self.assertEqual(ultimate_reconstruct("$VL N"), "$VLN")
        self.assertEqual(ultimate_reconstruct("$P GY"), "$PGY")
        self.assertEqual(ultimate_reconstruct("$NVD A"), "$NVDA")
        self.assertEqual(ultimate_reconstruct("$PO E T"), "$POET")

    def test_smashed_tickers(self):
        self.assertEqual(ultimate_reconstruct("$PGY$NVDA"), "$PGY $NVDA")
        self.assertEqual(ultimate_reconstruct("$PGY$NVDA$DELL"), "$PGY $NVDA $DELL")

    def test_smashed_split_tickers(self):
        # User example: $PG Y$NVD A$DELL $MS FT$AAP Lhello
        # Should ideally be: $PGY $NVDA $DELL $MSFT $AAPL hello
        # We handle fragments first, then smashes, then trailing words
        text = "$PG Y$NVD A$DELL $MS FT$AAP Lhello"
        expected = "$PGY $NVDA $DELL $MSFT $AAPL hello"
        self.assertEqual(ultimate_reconstruct(text), expected)

    def test_mixed_case(self):
        self.assertEqual(ultimate_reconstruct("$pg y$nv dahello"), "$PGY $NVDA hello")
        self.assertEqual(ultimate_reconstruct("$pgy$nvdahello"), "$PGY $NVDA hello")

    def test_symbols_and_slashes(self):
        self.assertEqual(ultimate_reconstruct("$PGY/hello"), "$PGY /hello")
        self.assertEqual(ultimate_reconstruct("$P GY / hello"), "$PGY / hello")
        self.assertEqual(ultimate_reconstruct("$pg y/nv dahello"), "$PGY /NVDA hello")

    def test_no_corruption(self):
        self.assertEqual(ultimate_reconstruct("I love $NVDA"), "I love $NVDA")
        self.assertEqual(ultimate_reconstruct("The price of $OSS is up"), "The price of $OSS is up")

if __name__ == "__main__":
    unittest.main()
