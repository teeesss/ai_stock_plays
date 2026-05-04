"""
GIGACPO Social Intelligence Engine
Aggregates X posts, calculates buzz, and handles visual intel preservation.
Modular and callable from any conductor.
"""

import datetime
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"


class SocialIntelEngine:
    @staticmethod
    def rebuild():
        print("REBUILDING SOCIAL INTEL MODULE...")

        # 1. Preserve OCR data
        master_path = DB_DIR / "x_intel_master.json"
        existing_visual_mentions = {}
        existing_visual_ts = None

        if master_path.exists():
            try:
                old = json.loads(master_path.read_text(encoding="utf-8"))
                existing_visual_mentions = old.get("visual_mentions", {})
                existing_visual_ts = old.get("visual_last_updated")
            except:
                pass

        # 2. Aggregate user files
        all_posts = []
        user_files = [f for f in DB_DIR.glob("x_intel_*.json") if "master" not in f.name]

        now = datetime.datetime.now(datetime.timezone.utc)
        periods = {
            "24h": now.timestamp() - 86400,
            "7d": now.timestamp() - 86400 * 7,
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
                    tickers = set(re.findall(r"\$([A-Z]{2,12})(?![A-Z])", txt.upper()))
                    try:
                        ts = datetime.datetime.fromisoformat(p.get("timestamp", "")).timestamp()
                    except:
                        ts = 0

                    for t in tickers:
                        if t not in buzz:
                            buzz[t] = {"24h": 0, "7d": 0, "30d": 0, "total": 0}
                        buzz[t]["total"] += 1
                        for k, cutoff in periods.items():
                            if ts > cutoff:
                                buzz[t][k] += 1
            except:
                pass

        # 3. Dedup & Sort
        all_posts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        seen = set()
        deduped = []
        for p in all_posts:
            if p["id"] not in seen:
                deduped.append(p)
                seen.add(p["id"])

        # 4. Build Payload
        payload = {
            "updated_at": now.isoformat(),
            "posts": deduped,
            "buzz": buzz,
            "visual_mentions": existing_visual_mentions,
            "visual_last_updated": existing_visual_ts,
        }

        # 5. Write Files
        master_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        # Build stripped JS version for performance
        stripped_posts = []
        for p in deduped:
            c = p.copy()
            if "images" in c:
                del c["images"]
            if "visual_intel" in c:
                del c["visual_intel"]
            stripped_posts.append(c)

        bridge_payload = payload.copy()
        bridge_payload["posts"] = stripped_posts

        js_content = "window.X_INTEL_MODULE = " + json.dumps(bridge_payload) + ";"
        (DB_DIR / "intel.js").write_text(js_content, encoding="utf-8")
        (ROOT / "intel.js").write_text(js_content, encoding="utf-8")

        # V30.4.15: Restore legacy master naming for template compatibility
        (DB_DIR / "x_intel_master.js").write_text(js_content, encoding="utf-8")
        (ROOT / "x_intel_master.js").write_text(js_content, encoding="utf-8")

        print(f"Social Intel Success: {len(deduped)} posts aggregated.")
        return payload
