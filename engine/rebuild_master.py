"""
engine/rebuild_master.py
========================
Conducts a synchronized rebuild of all terminal endpoints (Root, AI).
Ensures any shared data updates are propagated to all dashboard_data.js files.
"""
from pipeline_orchestrator import PipelineOrchestrator

if __name__ == "__main__":
    print("[MASTER] Orchestrating Global Terminal Refresh...")
    # Rebuild Root Ecosystem (CPO/Semi)
    PipelineOrchestrator(terminal_type="root").process().deploy()
    
    # Rebuild AI/Crypto Ecosystem
    PipelineOrchestrator(terminal_type="ai").process().deploy()
    
    print("[MASTER] Global Rebuild Complete.")