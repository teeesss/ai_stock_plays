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
log = logging.getLogger("x_intel_instant")

USERS = ["aleabitoreddit", "PhotonCap", "KawzInvests"]
SCRAPER_SCRIPT = ROOT / "engine" / "x_intel_deep_scraper.py"
REMOTE_SYNC_SCRIPT = ROOT / "engine" / "remote_sync.py"

def instant_sync():
    log.info("=" * 60)
    log.info("⚡ INSTANT INTELLIGENCE REFRESH INITIATED")
    log.info(f"Targets: {', '.join(USERS)}")
    log.info("=" * 60)

    overall_success = True
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
            overall_success = False

    if overall_success:
        log.info("\n" + "=" * 60)
        log.info("🚀 SYNC SUCCESSFUL — INITIATING REMOTE UPLOAD")
        log.info("=" * 60)
        try:
            subprocess.run(
                [sys.executable, str(REMOTE_SYNC_SCRIPT)],
                cwd=str(ROOT),
                check=True
            )
            log.info("✅ REMOTE UPLOAD COMPLETE")
        except subprocess.CalledProcessError as e:
            log.error(f"❌ REMOTE UPLOAD FAILED (Code: {e.returncode})")
    else:
        log.warning("\n" + "!" * 60)
        log.warning("⚠️ SYNC HAD ERRORS — SKIPPING REMOTE UPLOAD")
        log.warning("!" * 60)

    log.info("\n" + "=" * 60)
    log.info("⚡ INSTANT SYNC COMPLETE")
    log.info("=" * 60)

if __name__ == "__main__":
    instant_sync()
