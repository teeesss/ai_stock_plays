import concurrent.futures
import io
import json

# ─────────────────────────────────────────────────────────
# V12.6 HYPER-DRIVE TURBINE (CLEAN MODE)
# No prefixes. Higher speed. No re-translation.
# ─────────────────────────────────────────────────────────
# Robust UTF-8 handling for Windows
import logging
import re
import sys
from pathlib import Path

from deep_translator import GoogleTranslator

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        # Fallback for old Python versions
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

# Configure primary logging to handle Unicode safely
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

# Suppress noisy/broken logging from sub-modules that trigger charmap errors
logging.getLogger("argostranslate").setLevel(logging.WARNING)
logging.getLogger("stanza").setLevel(logging.WARNING)

# Expanded CJK regex - covers Korean Hangul, Japanese Hiragana/Katakana, Chinese CJK Unified,
# CJK Compatibility Ideographs, Fullwidth Latin (used in Korean posts), and Korean punctuation.
FOREIGN_REGEX = re.compile(
    r"[\u4e00-\u9fff"  # CJK Unified Ideographs (Chinese/Japanese Kanji)
    r"\u3400-\u4dbf"  # CJK Extension A
    r"\u3040-\u309f"  # Hiragana
    r"\u30a0-\u30ff"  # Katakana
    r"\uac00-\ud7af"  # Korean Hangul Syllables
    r"\u1100-\u11ff"  # Hangul Jamo
    r"\ua960-\ua97f"  # Hangul Jamo Extended-A
    r"\ud7b0-\ud7ff"  # Hangul Jamo Extended-B
    r"\uff01-\uff60"  # Fullwidth Latin & punctuation (common in Korean posts)
    r"]"
)

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"
CACHE_FILE = DB_DIR / "translation_cache.json"

# Local Translator Init
LOCAL_TRANSLATOR = None
try:
    import argostranslate.package
    import argostranslate.translate

    LOCAL_TRANSLATOR = argostranslate.translate
except ImportError:
    pass


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def save_cache(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def apply_cache_to_files(cache: dict):
    files = list(DB_DIR.glob("x_intel_*.json"))
    for f in files:
        if "master" in f.name:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            changed = False
            for item in data:
                pid = str(item.get("id"))
                # Use raw_text as detection source - it is never overwritten by translation
                source_text = item.get("raw_text") or item.get("text", "")
                if pid in cache:
                    # Only update text if the raw/original still contains foreign chars
                    # (guards against applying stale cache entries to already-translated posts)
                    if FOREIGN_REGEX.search(source_text):
                        item["text"] = cache[pid]
                        changed = True
            if changed:
                f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except:
            pass


def translate_single(item_data, cache):
    post_id, text, src_lang, argos_code = item_data

    if post_id in cache:
        return post_id, cache[post_id]

    # Hyper-Speed Local Argos
    if LOCAL_TRANSLATOR:
        try:
            translated = LOCAL_TRANSLATOR.translate(text, argos_code, "en")
            if translated:
                return post_id, translated.strip()
        except:
            pass

    # Fallback to API
    try:
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        if translated:
            return post_id, translated.strip()
    except:
        return post_id, None


def translate():
    print("=" * 60, flush=True)
    print("V12.6 HYPER-DRIVE TURBINE (CLEAN MODE)", flush=True)
    print("=" * 60, flush=True)

    cache = load_cache()
    files = list(DB_DIR.glob("x_intel_*.json"))

    # Pre-Flush
    apply_cache_to_files(cache)

    all_tasks = []
    for f in files:
        if "master" in f.name:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for item in data:
                # CRITICAL: use raw_text as detection source, NOT text.
                # text may already be English (translated); raw_text is the original scraped content.
                source_text = item.get("raw_text") or item.get("text", "")
                post_id = str(item.get("id"))

                # Work required: raw source has foreign chars AND not cached yet
                if FOREIGN_REGEX.search(source_text) and post_id not in cache:
                    # Detect lang from raw source
                    src_lang = "korean"
                    argos_code = "ko"
                    if re.search(r"[\u3040-\u30ff]", source_text):
                        src_lang = "japanese"
                        argos_code = "ja"
                    elif re.search(r"[\u4e00-\u9fff\u3400-\u4dbf]", source_text):
                        src_lang = "chinese simplified"
                        argos_code = "zh"

                    all_tasks.append((post_id, source_text, src_lang, argos_code))
        except:
            continue

    total = len(all_tasks)
    if total == 0:
        print("Everything already translated.", flush=True)
    else:
        print(f"Crunching {total} remaining translations (16 Workers)...", flush=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            future_to_id = {
                executor.submit(translate_single, task, cache): task[0] for task in all_tasks
            }
            count = 0
            for future in concurrent.futures.as_completed(future_to_id):
                try:
                    res = future.result()
                    if res:
                        post_id, result = res
                        if result:
                            cache[post_id] = result
                except:
                    pass

                count += 1
                if count % 100 == 0:
                    print(f"  Progress: {count}/{total} (Batch Flush)", flush=True)
                    save_cache(cache)
                    apply_cache_to_files(cache)

    save_cache(cache)
    apply_cache_to_files(cache)
    print("\nHYPER-DRIVE COMPLETED. ALL DATABASE FILES CLEANED AND UPDATED.", flush=True)


if __name__ == "__main__":
    translate()
