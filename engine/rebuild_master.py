import json
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"

def rebuild_master():
    print("REBUILDING MASTER INTEL BRIDGE...")
    all_posts = []
    
    # Load all user databases
    user_files = list(DB_DIR.glob("x_intel_*.json"))
    # Exclude master
    user_files = [f for f in user_files if "master" not in f.name]
    
    ticker_counts = {}
    
    for f in user_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for p in data:
                all_posts.append(p)
                # Count tickers for "trending" (Buzz)
                txt = p.get("text", "")
                tickers = list(set(re.findall(r'\$([A-Z]{2,10})', txt)))
                for t in tickers:
                    ticker_counts[t] = ticker_counts.get(t, 0) + 1
        except Exception as e:
            print(f"Error loading {f.name}: {e}")

    # Sort by timestamp (newest first)
    all_posts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Get top tickers (Buzz)
    buzz = [{"ticker": k, "count": v} for k, v in sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:50]]

    payload = {
        "updated_at": datetime.now().isoformat(),
        "posts": all_posts,
        "buzz": buzz
    }

    # Save master JSON
    master_path = DB_DIR / "x_intel_master.json"
    master_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save intel.js bridge
    js_content = "window.X_INTEL_MODULE = " + json.dumps(payload, ensure_ascii=False) + ";"
    (DB_DIR / "intel.js").write_text(js_content, encoding="utf-8")
    (ROOT / "intel.js").write_text(js_content, encoding="utf-8")

    print(f"COMPLETE: {len(all_posts)} posts | {len(buzz)} tickers mapped.")

if __name__ == "__main__":
    rebuild_master()
