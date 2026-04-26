import io
import json
import logging
import re
import sys
from pathlib import Path

import easyocr

# Ensure UTF-8 output
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# PATHS
ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"
MASTER_INTEL = DB_DIR / "x_intel_master.json"
PROCESSED_LOG = DB_DIR / "processed_images.json"
MASTER_DATA = DB_DIR / "CPO_MASTER_DATA.json"

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def load_master_tickers():
    try:
        with open(MASTER_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.keys())
    except Exception as e:
        log.error(f"Error loading master tickers: {e}")
        return set()


def update_user_file(user, post_id, finding):
    user_file = DB_DIR / f"x_intel_{user}.json"
    if not user_file.exists():
        return

    try:
        with open(user_file, "r", encoding="utf-8") as f:
            posts = json.load(f)

        updated = False
        for post in posts:
            if str(post.get("id")) == str(post_id):
                visual_intel = post.get("visual_intel", [])
                # Avoid duplicates
                if not any(v["image"] == finding["image"] for v in visual_intel):
                    visual_intel.append(finding)
                    post["visual_intel"] = visual_intel
                    updated = True
                break

        if updated:
            with open(user_file, "w", encoding="utf-8") as f:
                json.dump(posts, f, indent=2)
    except Exception as e:
        log.error(f"Failed to update user file {user_file}: {e}")


def analyze_images():
    if not MASTER_INTEL.exists():
        log.error(f"Master intel not found at {MASTER_INTEL}")
        return

    log.info("Initializing EasyOCR...")
    try:
        reader = easyocr.Reader(["en"])
    except Exception as e:
        log.error(f"Failed to init EasyOCR: {e}")
        return

    tickers_whitelist = load_master_tickers()

    # Load Master Intel (we use this to find what to process)
    with open(MASTER_INTEL, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    processed_state = {}
    if PROCESSED_LOG.exists():
        try:
            with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
                processed_state = json.load(f)
        except:
            pass

    posts = master_data.get("posts", [])
    # Process newest first
    posts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    processed_count = 0

    for post in posts:
        username = post.get("username")
        post_id = post.get("id")
        images = post.get("images", [])
        if not images:
            continue

        for img_path_rel in images:
            img_path = ROOT / img_path_rel
            if not img_path.exists():
                continue

            img_id = str(img_path_rel)
            if img_id in processed_state:
                # Still ensure the finding is in the post (master might have been cleared)
                finding = processed_state[img_id]
                update_user_file(username, post_id, finding)
                continue

            # No limit - process everything in the queue to ensure 100% coverage
            # as requested in V15.5 Hardening.

            log.info(f"[{processed_count+1}/Batch] OCR: {img_path_rel}")
            try:
                results = reader.readtext(str(img_path), detail=0)
                text = " ".join(results)

                found_tickers = set(re.findall(r"\$([A-Z]{2,10})", text))
                for word in re.findall(r"\b[A-Z]{2,10}\b", text):
                    if word in tickers_whitelist:
                        found_tickers.add(word)

                finding = {
                    "image": str(img_path_rel),
                    "text": text,
                    "tickers": list(found_tickers),
                }

                # Update State and User File
                processed_state[img_id] = finding
                update_user_file(username, post_id, finding)

                processed_count += 1

                # Checkpoint State
                if processed_count % 5 == 0:
                    with open(PROCESSED_LOG, "w", encoding="utf-8") as f:
                        json.dump(processed_state, f, indent=2)

            except Exception as e:
                log.error(f"Failed to process {img_path}: {e}")

    # Final save
    with open(PROCESSED_LOG, "w", encoding="utf-8") as f:
        json.dump(processed_state, f, indent=2)

    log.info("Visual Intelligence Sync Complete.")
    log.info("Triggering Master Rebuild to reflect visual changes...")
    try:
        from x_intel_deep_scraper import rebuild_master

        rebuild_master()
    except Exception as e:
        log.error(f"Rebuild failed: {e}")


if __name__ == "__main__":
    analyze_images()
