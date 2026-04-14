"""
init_scanned_days.py — Bootstrap scanned_days.json from existing post timestamps.
Any day that has at least 1 post in the JSON is marked as "already scanned."
Run ONCE after migrate_v9.py.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

DB_DIR = Path("z:/COS_Stock_Plays/database")
SCANNED_FILE = DB_DIR / "scanned_days.json"
FORENSIC_START = "2025-10-01"

USERS = ["aleabitoreddit", "PhotonCap", "KawzInvests"]

# Load existing registry if any
registry = {}
if SCANNED_FILE.exists():
    try:
        registry = json.loads(SCANNED_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass

for user in USERS:
    file = DB_DIR / f"x_intel_{user}.json"
    if not file.exists():
        print(f"  SKIP @{user} — file not found")
        continue

    raw = json.loads(file.read_text(encoding="utf-8"))
    posts = raw if isinstance(raw, list) else raw.get("posts", [])

    # Collect all dates that have posts
    post_dates = set()
    for p in posts:
        try:
            ts = p.get("timestamp", "")
            if ts:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                post_dates.add(dt.strftime("%Y-%m-%d"))
        except Exception:
            pass

    # Merge with existing registry
    existing = set(registry.get(user, []))
    merged = sorted(existing | post_dates)
    registry[user] = merged

    print(f"  @{user}: {len(merged)} days marked as scanned "
          f"({len(post_dates)} from posts, {len(existing)} pre-existing)")

# Save
SCANNED_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
print(f"\nSaved -> {SCANNED_FILE}")
print("Note: Days with 0 posts but genuinely scraped will be added by the scraper going forward.")
