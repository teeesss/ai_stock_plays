import logging
import sys
from pathlib import Path

# V28: Setup Logging BEFORE any local imports that might hijack root
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("master")

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from pipeline_orchestrator import PipelineOrchestrator

if __name__ == "__main__":
    log.info("[MASTER] Orchestrating Global Terminal Refresh...")
    # Rebuild Root Ecosystem (CPO/Semi)
    PipelineOrchestrator(terminal_type="root").process().deploy()

    # Rebuild AI/Crypto Ecosystem
    PipelineOrchestrator(terminal_type="ai").process().deploy()

    log.info("[MASTER] Global Rebuild Complete.")
