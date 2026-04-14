"""
x_intel_instant_sync.py
=======================
Immediate, sequential sync for all users.
Bypasses the random jitter of the daily sync script.
Use this for manual 'refresh-now' operations.
"""

import sys
import logging
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("x_intel_instant")

USERS = ["aleabitoreddit", "PhotonCap", "KawzInvests"]
ROOT = Path(__file__).parent.parent
SCRAPER_SCRIPT = ROOT / "engine" / "x_intel_deep_scraper.py"

def instant_sync():
    log.info("=" * 60)
    log.info("⚡ INSTANT INTELLIGENCE REFRESH INITIATED")
    log.info(f"Targets: {', '.join(USERS)}")
    log.info("=" * 60)

    for idx, user in enumerate(USERS):
        log.info(f"\n[{idx+1}/{len(USERS)}] Synchronizing @{user}...")
        try:
            # Force sequential execution without jitter
            subprocess.run(
                [sys.executable, str(SCRAPER_SCRIPT), "--username", user],
                cwd=str(ROOT),
                check=True
            )
            log.info(f"✅ @{user} synced.")
        except subprocess.CalledProcessError as e:
            log.error(f"❌ Failed @{user} (Code: {e.returncode})")

    log.info("\n" + "=" * 60)
    log.info("⚡ INSTANT SYNC COMPLETE")
    log.info("=" * 60)

if __name__ == "__main__":
    instant_sync()
