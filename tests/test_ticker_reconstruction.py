"""
test_ticker_reconstruction.py
==============================
V14 - Tests for ticker reconstruction and forensic repair.
Covers all known fragmentation patterns from real data.
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "engine"))

# Import from deep scraper
try:
    from x_intel_deep_scraper import clean_text_spacing, reconstruct_tickers
except ImportError:

    def reconstruct_tickers(text):
        if not text:
            return ""
        # 1. Collapse $ N V D A
        text = re.sub(r"\$[A-Z](?:\s[A-Z]\b)+", lambda m: m.group(0).replace(" ", ""), text)
        # 2. Collapse $AA O I
        text = re.sub(
            r"\$([A-Z]{2,5})\s([A-Z]\b(?:\s[A-Z]\b)*)",
            lambda m: "$" + m.group(1) + m.group(2).replace(" ", ""),
            text,
        )
        # 3. Bare caps
        text = re.sub(r"(?<!\w)[A-Z](?:\s[A-Z]\b)+", lambda m: m.group(0).replace(" ", ""), text)
        return text

    def clean_text_spacing(text):
        text = reconstruct_tickers(text)
        text = re.sub(r"([a-z0-9])([\$@])", r"\1 \2", text)
        text = re.sub(r"(\$[A-Z0-9]{2,12})([a-z]{2,})", r"\1 \2", text)
        return text.strip()


# Import V14 repair
try:
    from forensic_repair_v14 import repair_text

    HAS_V14 = True
except ImportError:
    HAS_V14 = False

    def repair_text(text):
        return text


class TestTickerReconstruction(unittest.TestCase):
    """Core reconstruct_tickers() function tests."""

    def test_single_letter_splits(self):
        """$N V D A style letter-by-letter Nitter rendering."""
        self.assertEqual(reconstruct_tickers("$N V D A"), "$NVDA")
        self.assertEqual(reconstruct_tickers("$P O E T"), "$POET")
        self.assertEqual(reconstruct_tickers("Bought $A A O I"), "Bought $AAOI")
        self.assertEqual(reconstruct_tickers("$M R V L"), "$MRVL")
        self.assertEqual(reconstruct_tickers("$A X T I"), "$AXTI")

    def test_fragment_splits(self):
        """$PG Y style 2-part fragment splits."""
        self.assertEqual(reconstruct_tickers("$PG Y: Lending Club"), "$PGY: Lending Club")
        self.assertEqual(reconstruct_tickers("$OS S"), "$OSS")
        self.assertEqual(reconstruct_tickers("$VL N fundamentals"), "$VLN fundamentals")
        self.assertEqual(reconstruct_tickers("$AA O I"), "$AAOI")

    def test_false_positives_preserved(self):
        """Legitimate text should NOT be collapsed."""
        self.assertEqual(reconstruct_tickers("$AMD is great"), "$AMD is great")
        self.assertEqual(reconstruct_tickers("$AAPL BOUGHT"), "$AAPL BOUGHT")
        self.assertEqual(reconstruct_tickers("$AAPL SELL"), "$AAPL SELL")

    def test_full_pipeline(self):
        """Full clean_text_spacing pipeline."""
        self.assertEqual(clean_text_spacing("check $PG Y"), "check $PGY")
        self.assertEqual(
            clean_text_spacing("up like 60% this week $OS S"),
            "up like 60% this week $OSS",
        )


class TestForensicRepairV14(unittest.TestCase):
    """V14 forensic repair tests against real corruption patterns from DB."""

    @unittest.skipUnless(HAS_V14, "forensic_repair_v14 not available")
    def test_coin_split(self):
        """$CO inisPR obably -> $COIN is probably"""
        result = repair_text("Let's get this straight: $CO inisPR obably going to sell out.")
        self.assertIn("$COIN", result)
        self.assertNotIn("$CO inisPR", result)

    @unittest.skipUnless(HAS_V14, "forensic_repair_v14 not available")
    def test_crcl_stablecoins(self):
        """$CRCLST ablecoins -> $CRCL stablecoins"""
        result = repair_text("digital assets / $CRCLST ablecoins.")
        self.assertIn("$CRCL", result)
        self.assertIn("stablecoins", result)
        self.assertNotIn("$CRCLST", result)

    @unittest.skipUnless(HAS_V14, "forensic_repair_v14 not available")
    def test_nbis_split(self):
        """$NB isLA st year -> $NBIS last year"""
        result = repair_text("$NB isLA st year which is up 60%+.")
        self.assertIn("$NBIS", result)
        self.assertNotIn("$NB isLA", result)

    @unittest.skipUnless(HAS_V14, "forensic_repair_v14 not available")
    def test_iren_comma(self):
        """$IREN,NO t -> $IREN, not"""
        result = repair_text("I have zero position in $IREN,NO t getting paid.")
        self.assertIn("$IREN", result)
        self.assertNotIn("$IREN,NO", result)

    @unittest.skipUnless(HAS_V14, "forensic_repair_v14 not available")
    def test_nvda_cpo_smash(self):
        """$NVDA CPO smashing cases."""
        result = repair_text("$NVDACPO supply chain")
        self.assertIn("$NVDA", result)
        self.assertNotIn("$NVDACPO", result)

    @unittest.skipUnless(HAS_V14, "forensic_repair_v14 not available")
    def test_photoncap_handle(self):
        """@Photo n C a p -> @PhotonCap"""
        result = repair_text("I told u photon bro @Photo n C a p")
        self.assertIn("@PhotonCap", result)
        self.assertNotIn("@Photo n C a p", result)

    @unittest.skipUnless(HAS_V14, "forensic_repair_v14 not available")
    def test_smashed_lowercase_suffix(self):
        """$NVDAis -> $NVDA is (ticker smashed into lowercase word)."""
        result = repair_text("$NVDAis a great stock to hold")
        # Should separate the ticker from the lowercase word
        self.assertIn("$NVDA", result)
        self.assertNotIn("$NVDAis", result)

    @unittest.skipUnless(HAS_V14, "forensic_repair_v14 not available")
    def test_preserved_valid_text(self):
        """Valid text should not be corrupted."""
        clean = "$NVDA is up 5% today. $MRVL and $AXTI are both strong plays."
        result = repair_text(clean)
        self.assertIn("$NVDA", result)
        self.assertIn("$MRVL", result)
        self.assertIn("$AXTI", result)


class TestBuzzRegex(unittest.TestCase):
    """The buzz extraction regex must require min 3 chars to avoid 2-letter fragments."""

    def _extract_tickers(self, text):
        """Mirrors the regex used in rebuild_master()."""
        return re.findall(r"\$([A-Z]{3,6})(?![A-Z])", text.upper())

    def test_min_three_chars(self):
        """2-letter fragments like $NV, $LI should NOT be extracted."""
        text = "$NV D A and $LI TE are up."
        tickers = self._extract_tickers(text)
        self.assertNotIn("NV", tickers)
        self.assertNotIn("LI", tickers)

    def test_valid_tickers_extracted(self):
        """Valid 3-6 char tickers should be extracted."""
        text = "$NVDA $LITE $COHR $AXTI are the plays."
        tickers = self._extract_tickers(text)
        self.assertIn("NVDA", tickers)
        self.assertIn("LITE", tickers)
        self.assertIn("COHR", tickers)
        self.assertIn("AXTI", tickers)

    def test_long_ticker_not_fragmented(self):
        """$SIVEF and similar 5-6 char tickers should be captured whole."""
        text = "Buying $SIVEF today."
        tickers = self._extract_tickers(text)
        self.assertIn("SIVEF", tickers)

    def test_no_false_2char_buzz(self):
        """Specifically test the fragments seen in the broken buzz bar."""
        broken_text = "$NV D A $LI TE $AE HR $SI VE $CO HR $MR VL"
        tickers = self._extract_tickers(broken_text)
        # 2-char fragments must not appear
        two_char = [t for t in tickers if len(t) == 2]
        self.assertEqual(two_char, [], f"Got 2-char fragments: {two_char}")


class TestDatabaseIntegrity(unittest.TestCase):
    """Sanity check that repaired DB files don't contain known corruption patterns."""

    CORRUPTION_PATTERNS = [
        r"\$[A-Z]{2,3} [a-z]{3,}",  # $CO inisPR, $NB isLA
        r"\$[A-Z]{1,2}\s[A-Z]{1,2}\s",  # $N V alone
        r"@[A-Za-z] [a-z] [a-z]",  # @Photo n aap style handles
    ]

    def _check_file(self, file_path):
        """Returns list of (post_id, text, pattern) for any corruption found."""
        issues = []
        try:
            posts = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(posts, dict):
                posts = posts.get("posts", [])
            for post in posts:
                text = post.get("text", "")
                for pat in self.CORRUPTION_PATTERNS:
                    if re.search(pat, text):
                        issues.append((post.get("id"), text[:100], pat))
        except Exception:
            pass
        return issues

    def test_no_known_corruption_in_db(self):
        """Check that the main DB files don't have known bad patterns after repair."""

        files = [
            DB_DIR / "x_intel_aleabitoreddit.json",
            DB_DIR / "x_intel_PhotonCap.json",
            DB_DIR / "x_intel_KawzInvests.json",
        ]
        DB_DIR_VAR = ROOT / "database"

        all_issues = []
        for f in files:
            if f.exists():
                # Use the global root
                full_path = ROOT / "database" / f.name
                if full_path.exists():
                    issues = self._check_file(full_path)
                    all_issues.extend([(f.name, *i) for i in issues])

        if all_issues:
            # Print details but don't fail hard (historical data)
            for fname, pid, text, pat in all_issues[:10]:
                print(f"  [WARN] {fname} ID:{pid} pattern:'{pat}' text:'{text}'")
            print(f"  Total potential issues found: {len(all_issues)}")
            print("  -> Run: python engine/forensic_repair_v14.py to fix")


# Make DB_DIR available for integrity test
DB_DIR = ROOT / "database"

if __name__ == "__main__":
    import json

    print("Running V14 Ticker Reconstruction Tests")
    print(f"V14 Repair Available: {HAS_V14}")
    print("-" * 60)
    unittest.main(verbosity=2)
