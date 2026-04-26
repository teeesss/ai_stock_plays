import asyncio
import json
import logging
import random
import sys
from pathlib import Path

# Add engine to path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "engine"))

try:
    from vx_rescue_fetcher import rescue_tweet
except ImportError:
    from engine.vx_rescue_fetcher import rescue_tweet

try:
    from curl_cffi import requests as curlr
except ImportError:
    import requests as curlr

# Configure logging
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "image_repair.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("image_repair")

DB_DIR = ROOT / "database"
IMG_DIR = ROOT / "images"


async def download_image(url, path):
    """Download image with stealth and delay."""
    try:
        # V26.1: Institutional stealth delay
        await asyncio.sleep(random.uniform(2.5, 5.5))

        resp = curlr.get(url, impersonate="chrome110", timeout=15)
        if resp.status_code == 200 and len(resp.content) > 500:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(resp.content)
            return True
        elif resp.status_code == 429:
            log.warning("  Rate limited (429). Sleeping 30s...")
            await asyncio.sleep(30)
    except Exception as e:
        log.error(f"  Download error: {e}")
    return False


async def repair_user_images(username):
    user_file = DB_DIR / f"x_intel_{username}.json"
    if not user_file.exists():
        log.warning(f"User file not found: {user_file}")
        return

    log.info(f"Scanning @{username} for missing images...")
    posts = json.loads(user_file.read_text(encoding="utf-8"))

    user_img_dir = IMG_DIR / username
    user_img_dir.mkdir(parents=True, exist_ok=True)

    missing_count = 0
    repaired_count = 0

    for post in posts:
        image_urls = post.get("image_urls", [])
        if not image_urls:
            continue

        needs_repair = False
        for i, url in enumerate(image_urls):
            local_name = f"{post['id']}_{i}.jpg"
            local_path = user_img_dir / local_name

            if not local_path.exists():
                needs_repair = True
                break

        if needs_repair:
            missing_count += 1
            log.info(f"  Repairing {post['id']}...")

            # 1. Rescue to get fresh high-fi URLs (handles rate limiting internally)
            post = rescue_tweet(post)

            # 2. Re-download
            fresh_urls = post.get("image_urls", [])
            success_all = True
            for i, url in enumerate(fresh_urls):
                local_name = f"{post['id']}_{i}.jpg"
                local_path = user_img_dir / local_name
                if not local_path.exists():
                    if await download_image(url, local_path):
                        log.info(f"    [OK] Saved {local_name}")
                    else:
                        success_all = False

            if success_all:
                repaired_count += 1

    if missing_count > 0:
        log.info(
            f"@{username}: Found {missing_count} posts with missing images. Repaired {repaired_count}."
        )
        # Save updated user file (with new vx_rescued flags/urls)
        user_file.write_text(json.dumps(posts, indent=2, ensure_ascii=True), encoding="utf-8")
    else:
        log.info(f"@{username}: All images present.")


async def main():
    log.info("=" * 60)
    log.info("IMAGE REPAIR & RESCUE UTILITY (V26.1)")
    log.info("=" * 60)

    # Target users
    users = ["aleabitoreddit", "PhotonCap", "KawzInvests"]

    for user in users:
        await repair_user_images(user)

    log.info("=" * 60)
    log.info("REPAIR COMPLETE")
    log.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
