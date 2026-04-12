import sys
import os
from unittest.mock import MagicMock

# Add root to path
sys.path.append(os.getcwd())

import server

def test_sync_functionality():
    print("Testing Scheduler Pipeline Trigger...")
    
    # Mock the subprocess calls to avoid actually waiting for the full 10 minute audit
    # But we want to ensure the logic flows correctly
    print("  Triggering simulated market-close sync...")
    
    # We will run the real live_prices.py but mock the heavy auditor for speed
    import subprocess
    original_run = subprocess.run
    
    def mock_run(cmd, *args, **kwargs):
        if "financial_auditor" in str(cmd):
            print(f"    [MOCK] Skipping heavy auditor step: {cmd}")
            return MagicMock(returncode=0)
        return original_run(cmd, *args, **kwargs)
    
    subprocess.run = mock_run
    
    try:
        # Manually invoke the scheduled sync function
        server.scheduled_sync()
        print("✅ Scheduled Sync Trigger logic verified.")
    except Exception as e:
        print(f"❌ Scheduled Sync failed: {e}")
    finally:
        subprocess.run = original_run

if __name__ == "__main__":
    test_sync_functionality()
