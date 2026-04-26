import asyncio
import sys
from pathlib import Path

# Add project root to sys path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from engine.pipeline_orchestrator import PipelineOrchestrator
from engine.remote_sync import RemoteSync
from engine.social_intel_engine import SocialIntelEngine
from engine.sync_news import run_sync as sync_news
from engine.visual_buzz_aggregator import run as run_visual_aggregator


def full_sync():
    print("==========================================")
    print("--- STARTING GLOBAL GIGACPO SYNC (V20) ---")
    print("==========================================")

    # 1. Aggregate Social Intel (Posts + Buzz)
    SocialIntelEngine.rebuild()

    # 1.5 Aggregate Visual Buzz (OCR + Images)
    run_visual_aggregator()

    # 1.6 Sync Yahoo News
    print("Syncing Yahoo News universe...")
    asyncio.run(sync_news())

    # 2. Rebuild AI Dashboard (Processes & Deploys)
    PipelineOrchestrator(terminal_type="ai").process().deploy()

    # 3. Rebuild Root Dashboard (Processes & Deploys)
    PipelineOrchestrator(terminal_type="root").process().deploy()

    # 4. Sync UI Index Files & Modules
    print("Deploying UI index and support files...")
    RemoteSync.sync_file(ROOT / "cpo_plays.html")
    RemoteSync.sync_file(ROOT / "AI" / "index.html")
    RemoteSync.sync_file(ROOT / "database" / "YAHOO_NEWS_MODULE.js")
    RemoteSync.sync_file(ROOT / "database" / "intel.js")
    RemoteSync.sync_file(ROOT / "database" / "live_prices.js")

    print("--- GLOBAL SYNC COMPLETE ---")


if __name__ == "__main__":
    full_sync()
