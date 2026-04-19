"""
GIGACPO MASTER REBUILD (ROOT)
DEPRECATED: Use engine/global_orchestrator.py for full sync.
This script now points to PipelineOrchestrator for modular logic.
"""
from pipeline_orchestrator import PipelineOrchestrator

if __name__ == "__main__":
    print("[DEPRECATED] Calling modular PipelineOrchestrator (ROOT)...")
    PipelineOrchestrator(terminal_type="root").process().deploy()
