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
log_file = LOG_DIR / "instant_sync.log"

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

def run_step(name, command, specific_log=None):
    """Runs a command as a subprocess and logs its output in real-time."""
    log.info(f"--- STARTING: {name} ---")
    if specific_log:
        log.info(f"    (Detailed output in logs/{specific_log.name})")
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            cwd=str(ROOT)
        )
        
        # We'll write to the main log AND the specific log if provided
        with open(log_file, 'a', encoding='utf-8') as main_f:
            spec_f = open(specific_log, 'w', encoding='utf-8') if specific_log else None
            try:
                for line in process.stdout:
                    print(line, end='', flush=True)
                    main_f.write(line)
                    if spec_f:
                        spec_f.write(line)
            finally:
                if spec_f:
                    spec_f.close()
        
        process.wait()
        return process.returncode == 0
    except Exception as e:
        log.error(f"Error running {name}: {e}")
        return False

def instant_sync():
    log.info("=" * 60)
    log.info("⚡ INSTANT INTELLIGENCE REFRESH INITIATED")
    log.info(f"Targets: {', '.join(USERS)}")
    log.info("=" * 60)

    overall_success = True
    # 1. SCRAPE USERS
    for idx, user in enumerate(USERS):
        log.info(f"\n[{idx+1}/{len(USERS)}] Synchronizing @{user}...")
        user_log = LOG_DIR / f"{user}_sync.log"
        cmd = [sys.executable, "engine/x_intel_deep_scraper.py", "--username", user]
        if not run_step(f"Scrape @{user}", cmd, specific_log=user_log):
            log.error(f"❌ Failed @{user}")
            overall_success = False
        else:
            log.info(f"✅ @{user} synced.")

    if not overall_success:
        log.warning("\n" + "!" * 60)
        log.warning("⚠️ SYNC HAD ERRORS — SKIPPING FURTHER STEPS")
        log.warning("!" * 60)
        return

    # 2. IMAGE ANALYSIS
    log.info("\n📸 STEP 2: ANALYZING NEW IMAGES...")
    if not run_step("Image Analysis", [sys.executable, "engine/image_analyzer.py"]):
        log.warning("⚠️ Image analysis encountered issues, but continuing...")

    # 3. VISUAL BUZZ AGGREGATION
    log.info("\n🐝 STEP 3: AGGREGATING VISUAL BUZZ...")
    if not run_step("Visual Buzz", [sys.executable, "engine/visual_buzz_aggregator.py"]):
        log.warning("⚠️ Visual buzz aggregation encountered issues, but continuing...")

    # 4. DOCUMENTATION & BRAIN UPDATE
    log.info("\n🧠 STEP 4: UPDATING DOCUMENTATION & BRAIN...")
    if not run_step("Brain Update", [sys.executable, "engine/generate_CPO_BRAIN.py"]):
        log.warning("⚠️ Brain update encountered issues, but continuing...")

    # 5. BUILD & REMOTE UPLOAD
    log.info("\n" + "=" * 60)
    log.info("🚀 SYNC SUCCESSFUL — INITIATING BUILD & REMOTE UPLOAD")
    log.info("=" * 60)
    
    # On Windows, npm is a .cmd file. subprocess.Popen(shell=True) or npm.cmd is needed.
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    if run_step("Build Bundle", [npm_cmd, "run", "build"]):
        if run_step("Remote Deploy", [npm_cmd, "run", "deploy"]):
            log.info("✅ REMOTE UPLOAD COMPLETE")
        else:
            log.error("❌ REMOTE UPLOAD FAILED")
    else:
        log.error("❌ BUILD FAILED")

    # 6. LIVE PRICE SYNC (Final Step)
    log.info("\n💹 STEP 6: REFRESHING LIVE PRICES...")
    if not run_step("Live Prices", [sys.executable, "engine/live_prices.py"]):
        log.warning("⚠️ Live price sync encountered issues.")

    log.info("\n" + "=" * 60)
    log.info("⚡ INSTANT SYNC COMPLETE")
    log.info("=" * 60)


if __name__ == "__main__":
    instant_sync()
