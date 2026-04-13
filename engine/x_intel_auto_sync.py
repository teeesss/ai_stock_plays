"""
engine/x_intel_auto_sync.py
==========================
Lightweight script for 3x daily updates of X intelligence.
Checks only the most recent posts for tracked users.
"""

import asyncio
import sys
from pathlib import Path

# Reuse the deep scraper logic but with restricted days/pages
sys.path.append(str(Path(__file__).parent))
import x_intel_deep_scraper as scraper

async def run_auto_sync():
    print("--- [GIGACPO] Social Intelligence Auto-Sync Started ---")
    users = ['KawzInvests', 'PhotonCap', 'aleabitoreddit']
    
    all_new = []
    for user in users:
        print(f"Syncing @{user}...")
        # Only check the last 3 days to keep it fast
        posts = await scraper.scrape_user_history(user, max_days=3)
        all_new.extend(posts)
        
    if all_new:
        scraper.save_master(all_new)
    else:
        print("No new posts discovered.")
    print("--- Auto-Sync Complete ---")

if __name__ == '__main__':
    asyncio.run(run_auto_sync())
