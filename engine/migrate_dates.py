import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("migrate_dates")


def parse_date_fixed(raw: str) -> datetime:
    """Parses nitter date strings with full precision."""
    now = datetime.now(timezone.utc)
    if not raw:
        return now
    try:
        # 'May 4, 2026 · 10:43 PM UTC'
        dt = datetime.strptime(raw, "%b %d, %Y · %I:%M %p UTC")
        return dt.replace(tzinfo=timezone.utc)
    except:
        try:
            # Fallback for just the date
            clean = raw.split("·")[0].strip()
            dt = datetime.strptime(clean, "%b %d, %Y")
            return dt.replace(tzinfo=timezone.utc)
        except:
            # Handle '5h', '20m', etc.
            m = re.match(r"(\d+)([hmd])", raw)
            if m:
                val, unit = int(m.group(1)), m.group(2)
                if unit == "h":
                    return now - timedelta(hours=val)
                if unit == "m":
                    return now - timedelta(minutes=val)
                if unit == "d":
                    return now - timedelta(days=val)
            return now


def migrate():
    db_dir = "database"
    for filename in os.listdir(db_dir):
        if (
            filename.startswith("x_intel_")
            and filename.endswith(".json")
            and filename != "x_intel_master.json"
        ):
            path = os.path.join(db_dir, filename)
            log.info(f"Migrating {path}...")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                posts = data.get("posts", [])
                modified = False
                for post in posts:
                    raw_date = post.get("raw_date", "")
                    old_ts = post.get("timestamp", "")
                    new_dt = parse_date_fixed(raw_date)
                    new_ts = new_dt.isoformat()

                    if old_ts != new_ts:
                        post["timestamp"] = new_ts
                        modified = True

                if modified:
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    log.info(f"Updated {len(posts)} posts in {filename}")
            except Exception as e:
                log.error(f"Failed to migrate {filename}: {e}")


if __name__ == "__main__":
    migrate()
    log.info("Migration complete. Now rebuilding master...")
    from x_intel_deep_scraper import rebuild_master

    rebuild_master()
