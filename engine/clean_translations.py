import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"
CACHE_FILE = DB_DIR / "translation_cache.json"

def clean_file(f):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        changed = False
        for item in data:
            if "text" in item and item["text"].startswith("[EN: Translation]"):
                item["text"] = item["text"].replace("[EN: Translation] ", "").replace("[EN: Translation]", "").strip()
                changed = True
        if changed:
            f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  Cleaned {f.name}")
    except Exception as e:
        print(f"  Error {f.name}: {e}")

def run_cleanup():
    print("Cleaning up translation prefixes...")
    
    # 1. Clean Cache
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        new_cache = {}
        for k, v in cache.items():
            new_cache[k] = v.replace("[EN: Translation] ", "").replace("[EN: Translation]", "").strip()
        CACHE_FILE.write_text(json.dumps(new_cache, indent=2, ensure_ascii=False), encoding="utf-8")
        print("  Cleaned translation_cache.json")

    # 2. Clean JSON Files
    files = list(DB_DIR.glob("x_intel_*.json"))
    for f in files:
        if "master" in f.name: continue
        clean_file(f)

    print("Cleanup complete.")

if __name__ == "__main__":
    run_cleanup()
