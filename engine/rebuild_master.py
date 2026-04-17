"""
rebuild_master.py
=================
Rebuilds x_intel_master.json + intel.js from all per-user files.

DURABILITY RULE:
  Preserves visual_mentions + visual_last_updated from the existing master
  so OCR aggregation data is NEVER silently lost on a rebuild.
"""
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"


def rebuild_master():
    print("REBUILDING MASTER INTEL BRIDGE...")

    # ── STEP 0: Preserve OCR data from existing master ─────────
    master_path = DB_DIR / "x_intel_master.json"
    existing_visual_mentions = {}
    existing_visual_ts = None
    if master_path.exists():
        try:
            old = json.loads(master_path.read_text(encoding="utf-8"))
            existing_visual_mentions = old.get("visual_mentions", {})
            existing_visual_ts = old.get("visual_last_updated")
            if existing_visual_mentions:
                print(f"  Preserved visual_mentions: {len(existing_visual_mentions)} tickers from previous run")
        except Exception as e:
            print(f"  Warning: could not read existing master for visual_mentions: {e}")

    # ── STEP 1: Aggregate user files ────────────────────────────
    all_posts = []
    user_files = [f for f in DB_DIR.glob("x_intel_*.json") if "master" not in f.name]

    now = datetime.now(timezone.utc)
    periods = {
        "24h": now.timestamp() - 86400,
        "7d":  now.timestamp() - 86400 * 7,
        "30d": now.timestamp() - 86400 * 30,
    }
    buzz = {}

    for f in user_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            posts_list = data if isinstance(data, list) else data.get("posts", [])
            for p in posts_list:
                all_posts.append(p)
                txt = p.get("text", "")
                tickers = set(re.findall(r'\$([A-Z]{2,12})(?![A-Z])', txt.upper()))
                try:
                    ts = datetime.fromisoformat(p.get("timestamp", "")).timestamp()
                except Exception:
                    ts = 0
                for t in tickers:
                    if t not in buzz:
                        buzz[t] = {"24h": 0, "7d": 0, "30d": 0, "total": 0}
                    buzz[t]["total"] += 1
                    for k, cutoff in periods.items():
                        if ts > cutoff:
                            buzz[t][k] += 1
        except Exception as e:
            print(f"Error loading {f.name}: {e}")

    # Sort + dedup by ID
    all_posts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    seen = set()
    deduped = []
    for p in all_posts:
        if p["id"] not in seen:
            deduped.append(p)
            seen.add(p["id"])
    all_posts = deduped

    # ── STEP 2: Build payload — inject preserved OCR data ───────
    # We strip image arrays from the JS bridge version to prevent production 404 lag
    def strip_assets(p):
        p_clean = p.copy()
        if "images" in p_clean: del p_clean["images"]
        if "visual_intel" in p_clean: del p_clean["visual_intel"]
        return p_clean

    stripped_posts = [strip_assets(p) for p in all_posts]

    payload = {
        "updated_at":          now.isoformat(),
        "posts":               all_posts, # Keep original in master.json
        "buzz":                buzz,
        "visual_mentions":     existing_visual_mentions,
        "visual_last_updated": existing_visual_ts,
    }

    # ── STEP 3: Write files ─────────────────────────────────────
    # Master JSON keeps full data (local research)
    master_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    # JS Bridge gets stripped data (dashboard performance)
    bridge_payload = payload.copy()
    bridge_payload["posts"] = stripped_posts
    
    js_content = "// GIGACPO Intelligence Data - Auto-generated (images stripped for performance)\nwindow.X_INTEL_MODULE = " \
                 + json.dumps(bridge_payload, ensure_ascii=True) + ";"
    (DB_DIR / "intel.js").write_text(js_content, encoding="utf-8")
    (ROOT / "intel.js").write_text(js_content, encoding="utf-8")

    print(f"COMPLETE: {len(all_posts)} posts | {len(buzz)} tickers | {len(existing_visual_mentions)} visual tickers preserved. JS Bridge cleaned.")


if __name__ == "__main__":
    rebuild_master()
