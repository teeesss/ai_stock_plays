import os
import sys
import unittest

# Ensure the script can find dependencies
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "research"))
sys.path.append(os.path.join(os.getcwd(), "engine"))

from ultimate_repair import ultimate_reconstruct_v12_2 as ultimate_reconstruct


class TestTickerRepair(unittest.TestCase):
    def test_split_tickers(self):
        # Using tickers actually in MASTER_TICKERS (AAOI, CRDO, AEHR)
        self.assertEqual(ultimate_reconstruct("$A AOI"), "$AAOI")
        self.assertEqual(ultimate_reconstruct("$C R D O"), "$CRDO")
        self.assertEqual(ultimate_reconstruct("$A EHR"), "$AEHR")
        self.assertEqual(ultimate_reconstruct("$P O E T"), "$POET")

    def test_smashed_tickers(self):
        self.assertEqual(ultimate_reconstruct("$AAOI$CRDO"), "$AAOI $CRDO")

    def test_smashed_split_tickers(self):
        text = "$A AOI$C R D O$DELL $MS FT$AAP Lhello"
        res = ultimate_reconstruct(text)
        self.assertIn("$AAOI", res)
        self.assertIn("$CRDO", res)

    def test_no_corruption(self):
        self.assertEqual(ultimate_reconstruct("I love $CRDO"), "I love $CRDO")
        self.assertEqual(ultimate_reconstruct("The price of $OSS is up"), "The price of $OSS is up")


if __name__ == "__main__":
    unittest.main()
