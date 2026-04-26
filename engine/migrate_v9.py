"""
migrate_v9.py - Step 1: Deduplicate + Backup all x_intel JSON files.
Keeps bare array format. Removes duplicate IDs. Backs up originals.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

DB_DIR = Path("z:/COS_Stock_Plays/database")
BACKUP_DIR = DB_DIR / "backup"
BACKUP_DIR.mkdir(exist_ok=True)

USERS = ["aleabitoreddit", "PhotonCap", "KawzInvests"]

for user in USERS:
    file = DB_DIR / f"x_intel_{user}.json"
    if not file.exists():
        print(f"  SKIP {user} - file not found")
        continue

    # Backup original
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"x_intel_{user}_{ts}.json"
    shutil.copy2(file, backup)
    print(f"  Backed up @{user} -> {backup.name}")

    # Load
    raw = json.loads(file.read_text(encoding="utf-8"))
    posts = raw if isinstance(raw, list) else raw.get("posts", [])

    before = len(posts)

    # Deduplicate by ID (keep first occurrence = newest due to sort order)
    seen = set()
    clean = []
    for p in posts:
        pid = p.get("id")
        if pid and pid not in seen:
            seen.add(pid)
            clean.append(p)

    # Sort newest first
    clean.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    after = len(clean)
    removed = before - after

    # Save back as bare array
    file.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  @{user}: {before} -> {after} posts ({removed} dupes removed)")

print("\nDone. All files cleaned. Backups in database/backup/")
