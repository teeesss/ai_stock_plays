import json
import re
import time
import sys
import io
import concurrent.futures
from pathlib import Path
from deep_translator import GoogleTranslator, MyMemoryTranslator

# ─────────────────────────────────────────────────────────
# V12.6 HYPER-DRIVE TURBINE (CLEAN MODE)
# No prefixes. Higher speed. No re-translation.
# ─────────────────────────────────────────────────────────

# Fix Windows console encoding
# Robust UTF-8 handling for Windows
try:
    if sys.platform == "win32" and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
except (AttributeError, ValueError, io.UnsupportedOperation):
    pass

FOREIGN_REGEX = re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]')

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
        if "master" in f.name: continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            changed = False
            for item in data:
                pid = str(item.get("id"))
                text = item.get("text", "")
                if pid in cache:
                    # Only update if the text still contains foreign chars (i.e. not yet translated in this file)
                    if FOREIGN_REGEX.search(text):
                        item["text"] = cache[pid]
                        changed = True
            if changed:
                f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except: pass

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
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        if translated:
            return post_id, translated.strip()
    except:
        return post_id, None

def translate():
    print("="*60, flush=True)
    print("V12.6 HYPER-DRIVE TURBINE (CLEAN MODE)", flush=True)
    print("="*60, flush=True)
    
    cache = load_cache()
    files = list(DB_DIR.glob("x_intel_*.json"))
    
    # Pre-Flush
    apply_cache_to_files(cache)

    all_tasks = []
    for f in files:
        if "master" in f.name: continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for item in data:
                text = item.get("text", "")
                post_id = str(item.get("id"))
                
                # If text contains foreign chars AND not in cache -> It's work
                if FOREIGN_REGEX.search(text) and post_id not in cache:
                    # Detect lang
                    src_lang = "korean"; argos_code = "ko"
                    if re.search(r'[\u3040-\u30ff]', text):
                        src_lang = "japanese"; argos_code = "ja"
                    elif re.search(r'[\u4e00-\u9fff]', text):
                        src_lang = "chinese simplified"; argos_code = "zh"
                    
                    all_tasks.append((post_id, text, src_lang, argos_code))
        except: continue

    total = len(all_tasks)
    if total == 0:
        print("Everything already translated.", flush=True)
    else:
        print(f"Crunching {total} remaining translations (16 Workers)...", flush=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            future_to_id = {executor.submit(translate_single, task, cache): task[0] for task in all_tasks}
            count = 0
            for future in concurrent.futures.as_completed(future_to_id):
                try:
                    res = future.result()
                    if res:
                        post_id, result = res
                        if result: cache[post_id] = result
                except: pass
                
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
