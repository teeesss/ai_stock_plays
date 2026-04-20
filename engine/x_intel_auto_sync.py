"""
engine/x_intel_auto_sync.py
==========================
Lightweight script for 3x daily updates of X intelligence.
Checks only the most recent posts for tracked users.
"""

import asyncio
import sys
from pathlib import Path

import logging

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError: pass

ROOT = Path(__file__).parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"{Path(__file__).stem}.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("x_intel_auto")

# Reuse the deep scraper logic but with restricted days/pages
sys.path.append(str(Path(__file__).parent))
import x_intel_deep_scraper as scraper

async def run_auto_sync():
    log.info("--- [GIGACPO] Social Intelligence Auto-Sync Started ---")
    users = ['KawzInvests', 'PhotonCap', 'aleabitoreddit']
    
    all_new = []
    for user in users:
        log.info(f"Syncing @{user}...")
        # Only check the last 3 days to keep it fast
        posts = await scraper.scrape_user_history(user, max_days=3)
        all_new.extend(posts)
        
    if all_new:
        scraper.save_master(all_new)
    else:
        log.info("No new posts discovered.")
    log.info("--- Auto-Sync Complete ---")

if __name__ == '__main__':
    asyncio.run(run_auto_sync())