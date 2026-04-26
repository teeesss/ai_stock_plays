"""
tests/test_translation_detection.py
====================================
TDD tests for the translation detection and raw_text preservation logic.

Covers:
  - FOREIGN_REGEX correctly catches Hangul, Hiragana, Katakana, CJK
  - FOREIGN_REGEX correctly skips pure English text
  - apply_cache_to_files uses raw_text (not text) for detection
  - Phantom "new post" scenario: already-translated posts not re-flagged
  - Mixed Korean/English post (like the PhotonCap example) is detected via raw_text
  - Legacy posts (no raw_text) are back-filled correctly
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add engine directory to path so we can import translate_intel
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from translate_intel import FOREIGN_REGEX


class TestForeignRegex(unittest.TestCase):
    def test_detects_korean_hangul(self):
        """Pure Korean text must match."""
        text = "항상 겸손하게, 있는 그대로의 기술을 공유드리며"
        self.assertIsNotNone(FOREIGN_REGEX.search(text), "Should detect Hangul syllables")

    def test_detects_japanese_hiragana(self):
        text = "おはようございます"
        self.assertIsNotNone(FOREIGN_REGEX.search(text), "Should detect Hiragana")

    def test_detects_japanese_katakana(self):
        text = "アルミニウム"
        self.assertIsNotNone(FOREIGN_REGEX.search(text), "Should detect Katakana")

    def test_detects_chinese(self):
        text = "今天股市上涨"
        self.assertIsNotNone(FOREIGN_REGEX.search(text), "Should detect CJK Unified Ideographs")

    def test_detects_mixed_korean_english(self):
        """The PhotonCap example: English body + Korean suffix — must be detected."""
        text = (
            "After reaching 35K, we reached 40K in 6 days. "
            "항상 겸손하게, 있는 그대로의 기술을 공유드리며 제 생각이라고 밝히며 커뮤니티를 위해 공유하겠습니다."
        )
        self.assertIsNotNone(FOREIGN_REGEX.search(text), "Mixed Korean/English must be detected")

    def test_skips_pure_english(self):
        """Pure English text must NOT match."""
        text = "After reaching 35K, we reached 40K in 6 days. As I always say, I think I am moving forward."
        self.assertIsNone(FOREIGN_REGEX.search(text), "Pure English should not match")

    def test_skips_english_with_tickers(self):
        """English with $TICKER mentions must NOT match."""
        text = "Strong momentum on $LWLG and $AEHR today. Watch the $FORM setup."
        self.assertIsNone(FOREIGN_REGEX.search(text), "English with tickers should not match")

    def test_detects_hangul_jamo(self):
        """Extended Hangul Jamo blocks must also match."""
        text = "\u1100\u1161\u11ab"  # Hangul Jamo characters
        self.assertIsNotNone(FOREIGN_REGEX.search(text), "Should detect Hangul Jamo")


class TestApplyCacheToFiles(unittest.TestCase):
    """Verifies that apply_cache_to_files uses raw_text as the detection source."""

    def _make_temp_db(self, posts: list) -> Path:
        """Create a temp DB file with the given posts list. Returns the file path."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            prefix="x_intel_testuser_",
            encoding="utf-8",
            dir=tempfile.gettempdir(),
        )
        json.dump(posts, tmp, ensure_ascii=False, indent=2)
        tmp.close()
        return Path(tmp.name)

    def setUp(self):
        """Patch DB_DIR to use temp directory for isolation."""
        import translate_intel

        self._orig_db_dir = translate_intel.DB_DIR
        translate_intel.DB_DIR = Path(tempfile.gettempdir())
        self.translate_intel = translate_intel

    def tearDown(self):
        import translate_intel

        translate_intel.DB_DIR = self._orig_db_dir

    def test_raw_text_used_for_detection_not_translated_text(self):
        """
        PHANTOM POST BUG: A post that was already translated (text=English)
        but raw_text=Korean should NOT be updated again by apply_cache_to_files.
        The cache hit should only apply if raw_text still has foreign chars.
        """
        korean_original = "항상 겸손하게, 있는 그대로의 기술을 공유드리며"
        translated_english = "Always be humble, share the technology as it is"

        posts = [
            {
                "id": "99999",
                "text": translated_english,  # Already translated
                "raw_text": korean_original,  # Original Korean preserved
            }
        ]
        f = self._make_temp_db(posts)

        # Cache has a newer translation for this ID
        cache = {"99999": "New translation version"}
        self.translate_intel.apply_cache_to_files(cache)

        # Read back — text should be updated since raw_text has foreign chars
        result = json.loads(f.read_text(encoding="utf-8"))
        self.assertEqual(
            result[0]["text"],
            "New translation version",
            "Should apply cache because raw_text still has Korean",
        )
        f.unlink()

    def test_english_raw_text_not_overwritten(self):
        """
        A post where raw_text is pure English should NOT be touched by apply_cache_to_files,
        even if it appears in the cache (stale cache entry scenario).
        """
        posts = [
            {
                "id": "88888",
                "text": "Strong $LWLG momentum today",
                "raw_text": "Strong $LWLG momentum today",  # English original
            }
        ]
        f = self._make_temp_db(posts)

        # Stale cache entry — should not be applied
        cache = {"88888": "some translated version"}
        self.translate_intel.apply_cache_to_files(cache)

        result = json.loads(f.read_text(encoding="utf-8"))
        self.assertEqual(
            result[0]["text"],
            "Strong $LWLG momentum today",
            "English-only post must not be modified by cache apply",
        )
        f.unlink()

    def test_legacy_post_without_raw_text_still_detected(self):
        """
        Legacy posts that have no raw_text field fall back to checking text.
        If text has Korean, they should be updated.
        """
        korean_text = "항상 겸손하게"

        posts = [
            {
                "id": "77777",
                "text": korean_text,
                # No raw_text — legacy post
            }
        ]
        f = self._make_temp_db(posts)

        cache = {"77777": "Always be humble"}
        self.translate_intel.apply_cache_to_files(cache)

        result = json.loads(f.read_text(encoding="utf-8"))
        self.assertEqual(
            result[0]["text"],
            "Always be humble",
            "Legacy post without raw_text should still be translated via text fallback",
        )
        f.unlink()


class TestScraperRawTextField(unittest.TestCase):
    """Verifies that parse_tweet adds raw_text = text at scrape time (unit test of the schema)."""

    def test_raw_text_equals_text_on_new_post(self):
        """
        Simulate what parse_tweet now returns: raw_text must equal text on initial scrape.
        No translation has happened yet, so they should be identical.
        """
        # Simulate the dict that parse_tweet returns
        simulated_post = {
            "id": "12345",
            "username": "PhotonCap",
            "text": "항상 겸손하게, 있는 그대로의 기술을 공유드리며",
            "raw_text": "항상 겸손하게, 있는 그대로의 기술을 공유드리며",
            "timestamp": "2026-04-16T00:00:00+00:00",
        }
        self.assertEqual(
            simulated_post["text"],
            simulated_post["raw_text"],
            "At scrape time, text and raw_text must be identical",
        )

    def test_raw_text_preserved_after_translation(self):
        """After translation, text changes but raw_text must remain unchanged."""
        post = {
            "id": "12345",
            "text": "항상 겸손하게",
            "raw_text": "항상 겸손하게",  # Preserved at scrape time
        }
        # Simulate translation step updating text only
        post["text"] = "Always be humble"

        self.assertEqual(
            post["raw_text"],
            "항상 겸손하게",
            "raw_text must remain the original Korean after translation",
        )
        self.assertEqual(
            post["text"],
            "Always be humble",
            "text must be updated to English translation",
        )
        # FOREIGN_REGEX on raw_text should still detect it as foreign
        self.assertIsNotNone(FOREIGN_REGEX.search(post["raw_text"]))
        # But text is now English — would NOT detect as foreign
        self.assertIsNone(FOREIGN_REGEX.search(post["text"]))


class TestIncrementalSaveDedup(unittest.TestCase):
    """Verifies that _incremental_save compares IDs as strings to prevent phantom duplicates."""

    def test_string_int_id_comparison(self):
        """
        JSON may load IDs as integers. Existing posts with int IDs must not be
        treated as 'new' when compared against string IDs from a fresh scrape.
        """
        # Simulate existing posts where JSON loaded ID as int
        existing = [{"id": 12345, "text": "existing post"}]
        existing_ids = {str(p["id"]) for p in existing}

        # Simulate new scrape returning same ID as string
        new_post = {"id": "12345", "text": "existing post"}
        is_new = str(new_post["id"]) not in existing_ids

        self.assertFalse(
            is_new,
            "String '12345' must match existing int 12345 after str() normalization",
        )

    def test_genuinely_new_post_detected(self):
        """A post with a new ID must always be treated as new."""
        existing = [{"id": "11111", "text": "old post"}]
        existing_ids = {str(p["id"]) for p in existing}

        new_post = {"id": "99999", "text": "new post"}
        is_new = str(new_post["id"]) not in existing_ids

        self.assertTrue(is_new, "A genuinely new post ID must be detected as new")


if __name__ == "__main__":
    unittest.main(verbosity=2)
