import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"


def build():
    print(f"Building production bundle in {DIST}...")

    # 1. Clean/Create dist folder
    if DIST.exists():
        shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(exist_ok=True)

    # 2. Copy Web Endpoints
    # Mapping: local_web_dir -> dist_dir
    web_endpoints = {
        "web/semi": ".",  # Root /stocks/
        "web/ai": "ai",  # /stocks/ai/
    }
    shared_assets = [
        "database/live_prices.js",
        "database/YAHOO_NEWS_MODULE.js",
        "database/x_intel_master.js",
    ]

    for web_rel, dist_rel in web_endpoints.items():
        src = ROOT / web_rel
        dst = DIST if dist_rel == "." else DIST / dist_rel

        if src.exists():
            dst.mkdir(parents=True, exist_ok=True)
            # Copy all files in the web endpoint directory (index.html, dashboard_data.js)
            for item in src.iterdir():
                if item.is_file() and not item.name.endswith("_template.html"):
                    shutil.copy2(item, dst / item.name)
                    print(f"  Copied {item.relative_to(ROOT)} -> dist/{dist_rel}/{item.name}")
        else:
            print(f"  Warning: {web_rel} not found, skipping.")

    # 3. Copy Shared Database Assets (mirrored structure)
    for asset in shared_assets:
        src = ROOT / asset
        dst = DIST / asset
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  Copied {asset} -> dist/{asset}")

    print("Build complete.")


if __name__ == "__main__":
    build()
