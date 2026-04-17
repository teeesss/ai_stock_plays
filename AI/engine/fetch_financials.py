import os
import sys
import json
import asyncio
from datetime import datetime

# Inject core engine path to reuse stealth_navigator and dependencies
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../engine')))

from financial_auditor import audit_financials

MASTER_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database/AI_MASTER_DATA.json'))

async def run_ai_audit():
    # We will just patch the MASTER_JSON_PATH globally in the imported module
    import financial_auditor as core_auditor
    core_auditor.MASTER_JSON_PATH = MASTER_JSON_PATH
    
    # We will override the generate API
    core_auditor.generate_brain_from_master = lambda path: print(f"Skipping brain generation for {path}")
    
    await core_auditor.audit_financials(None)

    # Trigger AI rebuild
    import rebuild_master
    rebuild_master.rebuild()

if __name__ == "__main__":
    try:
        asyncio.run(run_ai_audit())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Critical Error: {e}")
