import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"

def build():
    print(f"Building production bundle in {DIST}...")
    
    # 1. Clean/Create dist folder
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(exist_ok=True)
    (DIST / "database").mkdir(exist_ok=True)

    # 2. Files to copy
    # Mapping: local_path -> dist_path
    files = {
        "cpo_plays.html": "index.html",
        "database/dashboard_data.js": "database/dashboard_data.js",
        "database/live_prices.js": "database/live_prices.js",
        "database/intel.js": "intel.js", # Note: remote expects intel.js in root or database? 
                                          # remote_sync.py says: "database/intel.js": "intel.js"
    }

    # Verify what remote_sync.py does:
    # "cpo_plays.html": "index.html"
    # "database/dashboard_data.js": "database/dashboard_data.js"
    # "database/live_prices.js": "database/live_prices.js"
    # "database/intel.js": "intel.js"

    for local_rel, dist_rel in files.items():
        src = ROOT / local_rel
        dst = DIST / dist_rel
        
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  Copied {local_rel} -> dist/{dist_rel}")
        else:
            print(f"  Warning: {local_rel} not found, skipping.")

    print("Build complete.")

if __name__ == "__main__":
    build()
