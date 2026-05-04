"""
engine/x_intel_auto_sync.py
==========================
Lightweight script for 3x daily updates of X intelligence.
Checks only the most recent posts for tracked users.
"""

import asyncio
import logging
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

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
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("x_intel_auto")

# V28: Hierarchy Leader Dependency Check
try:
    from dependency_mgr import ensure_dependencies
except ImportError:
    from engine.dependency_mgr import ensure_dependencies
ensure_dependencies()

# Reuse the deep scraper logic but with restricted days/pages
sys.path.append(str(Path(__file__).parent))
import x_intel_deep_scraper as scraper


async def run_auto_sync():
    log.info("--- [GIGACPO] Social Intelligence Auto-Sync Started ---")
    users = ["KawzInvests", "PhotonCap", "aleabitoreddit"]

    for user in users:
        log.info(f"Syncing @{user}...")
        # Only check the last 3 days to keep it fast
        await scraper.scrape_user(user, max_days=3)

        # V30.4.15: Post-scrape hygiene
        scraper._deduplicate_file(user)
        try:
            from repair_tickers import repair_user

            repair_user(user)
        except Exception as e:
            log.warning(f"  Ticker repair failed for @{user}: {e}")

    log.info("Rebuilding master intelligence module...")
    scraper.rebuild_master()

    log.info("--- Auto-Sync Complete ---")


if __name__ == "__main__":
    asyncio.run(run_auto_sync())
