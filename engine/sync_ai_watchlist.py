import sys
import logging
import subprocess
from pathlib import Path

# engine/sync_ai_watchlist.py
ENGINE_DIR = Path(__file__).parent
PROJECT_ROOT = ENGINE_DIR.parent

logging.basicConfig(level=logging.INFO, format="[AI-SYNC] %(message)s")
log = logging.getLogger("ai_sync")

def run_step(name, cmd_args, cwd=PROJECT_ROOT):
    log.info(f"--- STARTING: {name} ---")
    try:
        subprocess.run([sys.executable] + cmd_args, cwd=str(cwd), check=True)
        log.info(f" [OK] {name} complete.")
        return True
    except Exception as e:
        log.error(f" [ERR] {name} failed: {e}")
        return False

def sync():
    log.info("=" * 60)
    log.info("🤖 AI WATCHLIST INDEPENDENT SYNC INITIATED")
    log.info("=" * 60)

    # 1. Refresh Live Prices (AI Tickers Only) - Note: Global prices typically fetched but can be isolated
    if not run_step("Live Prices", ["engine/live_prices.py", "--force"]):
        return

    # 2. OpenBB Supplement (Analyst data + 1Y Performance)
    if not run_step("OpenBB Supplement", ["engine/openbb_fetcher.py", "--force"]):
        return

    # 3. Modular Rebuild (AI Only)
    from engine.pipeline_orchestrator import PipelineOrchestrator
    try:
        log.info("--- STARTING: Modular AI Rebuild ---")
        PipelineOrchestrator("ai").process()
        log.info(" [OK] Modular AI Rebuild complete.")
    except Exception as e:
        log.error(f" [ERR] Modular rebuild failed: {e}")
        return

    # 4. Sync AI News
    if not run_step("News Sync", ["engine/sync_news.py"]):
        return

    # 5. Deploy to Remote (/stocks/ai/)
    log.info("\n🚀 INITIATING DEPLOYMENT...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    try:
        subprocess.run([npm_cmd, "run", "build"], cwd=str(PROJECT_ROOT), check=True)
        subprocess.run([npm_cmd, "run", "deploy"], cwd=str(PROJECT_ROOT), check=True)
        log.info(" [OK] AI DEPLOYMENT SUCCESSFUL")
    except Exception as e:
        log.error(f" [ERR] Deployment failed: {e}")

    log.info("\n" + "=" * 60)
    log.info("⚡ AI SYNC COMPLETE")
    log.info("=" * 60)

if __name__ == "__main__":
    sync()
