"""
GIGACPO Triple Sync Wrapper
===========================
The ultimate conductor for refreshing the intelligence universe.
1. Tweets (X/Nitter Scrape + Aggregate)
2. News (Yahoo News Sync)
3. OCR (Image Analysis + Visual Buzz)
4. Dual Deployment (Semi & AI Terminals)
"""

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

# Fix paths
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / "sync_triple.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("sync_triple")


def run_script(script_name, args=[]):
    script_path = ROOT / "engine" / script_name
    cmd = [sys.executable, str(script_path)] + args
    log.info(f"EXECUTING: {script_name} {' '.join(args)}")

    try:
        # We use subprocess.run to wait and check return code
        result = subprocess.run(cmd, check=True, cwd=str(ROOT))
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"[FAIL] FAILED: {script_name} (Exit code: {e.returncode})")
        return False
    except Exception as e:
        log.error(f"[FAIL] CRITICAL ERROR running {script_name}: {e}")
        return False


def sync_triple():
    parser = argparse.ArgumentParser(description="GIGACPO Triple Sync")
    parser.add_argument("--skip-ocr", action="store_true", help="Skip the slow Image OCR pass")
    parser.add_argument(
        "--skip-scrape", action="store_true", help="Skip fresh scraping (Rebuild only)"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Alias for --skip-ocr --skip-scrape (for quick UI fixes)",
    )
    args = parser.parse_args()

    if args.fast:
        args.skip_ocr = True
        args.skip_scrape = True

    start_time = time.time()
    log.info("=" * 60)
    log.info("TRIPLE SYNC INITIATED")
    log.info(
        f"Options: OCR={'OFF' if args.skip_ocr else 'ON'}, Scrape={'OFF' if args.skip_scrape else 'ON'}"
    )
    log.info("=" * 60)

    # 1. PULL TWEETS
    if not args.skip_scrape:
        log.info("\n[1/3] SYNCING TWEETS (X/NITTER)...")
        # We use instant sync logic for a thorough but focused pass
        if not run_script("x_intel_instant_sync.py"):
            log.warning("[WARN] Tweet sync had issues, but continuing...")
    else:
        log.info("\n[1/3] REBUILDING SOCIAL INTEL (SKIPPING SCRAPE)...")
        run_script("rebuild_master.py")  # This aggregates existing user JSONs

    # 2. PULL NEWS
    log.info("\n[2/3] SYNCING YAHOO NEWS...")
    if not run_script("sync_news.py"):
        log.warning("[WARN] News sync had issues, but continuing...")

    # 3. OCR PASS
    if not args.skip_ocr:
        log.info("\n[3/3] RUNNING IMAGE OCR ANALYSIS...")
        if not run_script("image_analyzer.py"):
            log.warning("[WARN] OCR analysis had issues, but continuing...")
        log.info("Aggregating visual buzz...")
        run_script("visual_buzz_aggregator.py")
    else:
        log.info("\n[3/3] SKIPPING OCR PASS.")

    # 4. DUAL DEPLOYMENT
    log.info("\n" + "=" * 60)
    log.info("INITIATING DUAL-WEB DEPLOYMENT")
    log.info("=" * 60)

    # We call PipelineOrchestrator via their specific main blocks (or we could call a tiny script)
    # Reusing the existing pattern: rebuild_master.py does root, so we just need a twin for AI or call PO.
    from engine.pipeline_orchestrator import PipelineOrchestrator

    log.info("Updating SEMI Terminal (/stocks)...")
    PipelineOrchestrator(terminal_type="root").process().deploy()

    log.info("Updating AI Terminal (/stocks/ai)...")
    PipelineOrchestrator(terminal_type="ai").process().deploy()

    duration = time.time() - start_time
    log.info("\n" + "=" * 60)
    log.info(f"TRIPLE SYNC COMPLETE in {duration:.1f}s")
    log.info("=" * 60)


if __name__ == "__main__":
    sync_triple()
