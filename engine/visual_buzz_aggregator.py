"""
visual_buzz_aggregator.py
=========================
Reads visual_intel arrays from all per-user JSON files.
Aggregates OCR-extracted ticker mentions per ticker.
Merges into x_intel_master.json's buzz structure as "visual_mentions".
Also rebuilds intel.js to expose this data to the dashboard.

Run after image_analyzer.py completes.
Called automatically by x_intel_daily_sync.py.
"""

import io
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# V28: Setup Logging BEFORE any local imports that might hijack root
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("visual_buzz")

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"

USER_FILES = []
USER_LIST_FILE = DB_DIR / "monitored_users.json"
if USER_LIST_FILE.exists():
    with open(USER_LIST_FILE, "r", encoding="utf-8") as f:
        usernames = json.load(f)
        USER_FILES = [f"x_intel_{u}.json" for u in usernames]
else:
    # Fallback to filesystem glob
    USER_FILES = [f.name for f in DB_DIR.glob("x_intel_*.json") if f.name != "x_intel_master.json"]

MASTER_TICKERS_PATH = DB_DIR / "CPO_MASTER_DATA.json"
MASTER_INTEL_PATH = DB_DIR / "x_intel_master.json"
INTEL_JS_PATH = DB_DIR / "intel.js"
ROOT_INTEL_JS = ROOT / "intel.js"


# V28: Auto-Dependency Guardian
try:
    try:
        from dependency_mgr import ensure_dependencies
    except ImportError:
        from engine.dependency_mgr import ensure_dependencies
    ensure_dependencies()
except ImportError:
    pass

try:
    from ticker_utils import load_master_tickers
except ImportError:
    from engine.ticker_utils import load_master_tickers


def aggregate_visual_buzz() -> dict:
    """
    Scan all user files for posts with visual_intel.
    For each visual_intel entry, extract tickers from:
      - finding['tickers'] list (already extracted by image_analyzer)
      - finding['text'] (regex fallback for missed tickers)
    Returns: dict[ticker -> {count, sample_texts}]
    """
    known_tickers = set(load_master_tickers())
    ticker_buzz = {}  # {ticker: {"count": int, "images": int, "sample_texts": []}}

    total_images_scanned = 0
    total_ticker_hits = 0

    for fname in USER_FILES:
        fpath = DB_DIR / fname
        if not fpath.exists():
            log.warning(f"User file not found: {fname}")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            posts = json.load(f)

        user = fname.replace("x_intel_", "").replace(".json", "")
        user_hits = 0

        for post in posts:
            vi = post.get("visual_intel", [])
            for finding in vi:
                total_images_scanned += 1
                text = finding.get("text", "")

                # Source 1: pre-extracted tickers list
                found = set(finding.get("tickers", []))

                # Source 2: regex on OCR text - cashtag style
                found.update(re.findall(r"\$([A-Z]{2,10})", text.upper()))

                # Source 3: whitelist match - bare uppercase words
                for word in re.findall(r"\b([A-Z]{2,10})\b", text.upper()):
                    if word in known_tickers:
                        # V28.3: Noise Suppression - Skip common short words misidentified as tickers
                        if len(word) <= 2 and word in [
                            "ON",
                            "BE",
                            "IT",
                            "IF",
                            "IS",
                            "OR",
                            "AN",
                            "BY",
                            "SO",
                            "DO",
                        ]:
                            continue
                        found.add(word)

                for ticker in found:
                    if ticker not in ticker_buzz:
                        ticker_buzz[ticker] = {
                            "count": 0,
                            "images": 0,
                            "sample_texts": [],
                        }
                    ticker_buzz[ticker]["count"] += 1
                    ticker_buzz[ticker]["images"] += 1
                    if len(ticker_buzz[ticker]["sample_texts"]) < 3:
                        snippet = text[:120].strip()
                        if snippet:
                            ticker_buzz[ticker]["sample_texts"].append(snippet)
                    user_hits += 1
                    total_ticker_hits += 1

        log.info(f"  {user}: {user_hits} visual ticker hits across visual_intel")

    log.info(f"Visual Buzz: {total_ticker_hits} hits from {total_images_scanned} analyzed images")
    log.info(f"Tickers found in images: {sorted(ticker_buzz.keys())}")
    return ticker_buzz


def merge_into_master(visual_buzz: dict):
    """
    Load x_intel_master.json and inject visual_mentions into the buzz section.
    Preserves existing tweet-based buzz counts.
    """
    if not MASTER_INTEL_PATH.exists():
        log.error(f"Master intel not found: {MASTER_INTEL_PATH}")
        return

    with open(MASTER_INTEL_PATH, "r", encoding="utf-8") as f:
        master = json.load(f)

    # Inject visual_mentions alongside existing buzz
    master["visual_mentions"] = visual_buzz
    master["visual_last_updated"] = datetime.now(timezone.utc).isoformat()

    # Save master JSON
    with open(MASTER_INTEL_PATH, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=True)
    log.info(f"Saved visual_mentions -> {MASTER_INTEL_PATH}")

    # Rebuild intel.js (dashboard bridge) - strip image arrays to prevent 404 storm
    def _strip(p):
        c = p.copy()
        c.pop("images", None)
        c.pop("visual_intel", None)
        return c

    bridge = {**master, "posts": [_strip(p) for p in master.get("posts", [])]}
    js_content = (
        "// GIGACPO Intelligence Data - images stripped for performance\nwindow.X_INTEL_MODULE = "
        + json.dumps(bridge)
        + ";"
    )
    with open(INTEL_JS_PATH, "w", encoding="utf-8") as f:
        f.write(js_content)
    with open(ROOT_INTEL_JS, "w", encoding="utf-8") as f:
        f.write(js_content)
    log.info(f"Rebuilt intel.js ({INTEL_JS_PATH.stat().st_size / 1024:.0f} KB) [stripped]")


def run():
    log.info("=" * 50)
    log.info("VISUAL BUZZ AGGREGATOR - Start")
    log.info("=" * 50)
    visual_buzz = aggregate_visual_buzz()
    if not visual_buzz:
        log.warning("No visual buzz data found. Ensure image_analyzer.py has run.")
        return
    merge_into_master(visual_buzz)
    log.info("VISUAL BUZZ AGGREGATOR - Complete")
    log.info(
        f"Top visual tickers: {sorted(visual_buzz.items(), key=lambda x: x[1]['count'], reverse=True)[:10]}"
    )


if __name__ == "__main__":
    run()
