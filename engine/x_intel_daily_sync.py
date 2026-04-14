"""
x_intel_daily_sync.py
=====================
Orchestrator for intra-day, staggered scraping across the entire user list.

Use this for your cron / Windows Task Scheduler setup!
Set your Windows Task Scheduler to trigger this file at your requested times:
3am, 5am, 7am, 8am, 9am, 10am, 11am, 12pm, 1pm, 2pm, 3pm, 4pm, 5pm, 7pm, 9pm, 11pm, 1am.

Features:
- Sweeps ALL predefined users automatically in one command.
- Injects a randomized jitter (between users and at start) to avoid pattern detection.
- Deep scraper ignores the cache for 'today' and 'yesterday', guaranteeing any intraday 
  tweets are caught while identically matching ones are silently deduplicated.
"""

import sys
import time
import random
import logging
import subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("x_intel_sync")

USERS = ["aleabitoreddit", "PhotonCap", "KawzInvests"]

ROOT = Path(__file__).parent.parent
ENGINE_DIR = ROOT / "engine"
SCRAPER_SCRIPT = ENGINE_DIR / "x_intel_deep_scraper.py"

def sync_all():
    log.info("=" * 60)
    log.info("V9.2 GLOBAL INTELLIGENCE SYNC INITIATED")
    log.info(f"Targets: {', '.join(USERS)}")
    log.info("=" * 60)

    # Global Jitter: Sleep up to 15 minutes before starting
    # (Comment this out if your cron job already provides the random stagger)
    initial_jitter = random.randint(30, 15 * 60)
    log.info(f"Applying initial random offset bounds ({initial_jitter} seconds)...")
    time.sleep(initial_jitter)

    for idx, user in enumerate(USERS):
        log.info(f"\n[{idx+1}/{len(USERS)}] Synchronizing @{user}...")
        
        try:
            # Call the main scraper as a subprocess ensuring isolated states
            result = subprocess.run(
                [sys.executable, str(SCRAPER_SCRIPT), "--username", user],
                cwd=str(ROOT),
                check=True
            )
            log.info(f"✅ @{user} complete.")
        except subprocess.CalledProcessError as e:
            log.error(f"❌ Failed to sync @{user} (Exit Code: {e.returncode})")

        # Stagger jitter between users: 2 to 10 minutes
        if idx < len(USERS) - 1:
            stagger = random.randint(120, 600)
            log.info(f"Applying intra-user stagger ({stagger} seconds)...")
            time.sleep(stagger)

    log.info("\n" + "=" * 60)
    log.info("GLOBAL INTELLIGENCE SYNC FINISHED")
    log.info("=" * 60)


if __name__ == "__main__":
    sync_all()
