"""
x_intel_instant_sync.py
=======================
Immediate, zero-jitter sync for manual execution.
Runs @aleabitoreddit, @PhotonCap, and @KawzInvests sequentially.
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
ENGINE_DIR = ROOT / "engine"
SCRAPER_SCRIPT = ENGINE_DIR / "x_intel_deep_scraper.py"

def sync_instant():
    log.info("=" * 60)
    log.info("INSTANT INTELLIGENCE SYNC INITIATED (No Jitter)")
    log.info(f"Targets: {', '.join(USERS)}")
    log.info("=" * 60)

    for idx, user in enumerate(USERS):
        log.info(f"\n[{idx+1}/{len(USERS)}] Instant Sync: @{user}")
        
        try:
            # Call the main scraper as a subprocess
            subprocess.run(
                [sys.executable, str(SCRAPER_SCRIPT), "--username", user],
                cwd=str(ROOT),
                check=True
            )
            log.info(f"✅ @{user} complete.")
        except subprocess.CalledProcessError as e:
            log.error(f"❌ Failed to sync @{user} (Exit Code: {e.returncode})")

    log.info("\n" + "=" * 60)
    log.info("INSTANT INTELLIGENCE SYNC FINISHED")
    log.info("=" * 60)


if __name__ == "__main__":
    sync_instant()
