"""
engine/x_intel_fetcher.py
========================
Scrapes X/Twitter posts via xcancel.com (Nitter instance) using StealthNavigator.
Avoids RSS whitelisting issues by scraping the HTML directly.

Usage: python engine/x_intel_fetcher.py --username KawzInvests
"""

import os
import json
import logging
import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup

# Import from current directory
try:
    from stealth_navigator import StealthNavigator
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from stealth_navigator import StealthNavigator

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError: pass

ROOT = Path(__file__).parent.parent
LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"{Path(__file__).stem}.log"

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

DB_DIR = ROOT / 'database'
DB_DIR.mkdir(exist_ok=True)

async def fetch_x_posts(username: str, limit: int = 10) -> list:
    url = f'https://xcancel.com/{username}'
    log.info(f"Fetching posts for @{username} from {url}")
    
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    
    posts = []
    try:
        page = await nav.context.new_page()
        # Set a common browser User-Agent to avoid 'RSS client' type blocks
        await page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        try:
            await page.goto(url, wait_until="load", timeout=30000)
        except:
            log.warning("Initial load timed out, trying to proceed...")
            
        # Give it a bit extra for dynamic content and redirects
        await asyncio.sleep(5)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Nitter / XCancel structure
        items = soup.select('.timeline-item')
        log.info(f"Found {len(items)} items on timeline.")
        
        for item in items:
            if 'pinned' in item.get('class', []):
                is_pinned = True
            else:
                is_pinned = False
                
            content_div = item.select_one('.tweet-content')
            date_link = item.select_one('.tweet-date a')
            stats_div = item.select_one('.tweet-stats') # optional
            
            if not content_div:
                continue
                
            text = content_div.get_text(strip=True)
            timestamp = date_link.get('title') if date_link else None
            tweet_url = f"https://xcancel.com{date_link.get('href')}" if date_link else None
            
            # Simple stats extraction
            stats = {}
            if stats_div:
                for stat in stats_div.select('.icon-container'):
                    icon = stat.select_one('span')
                    if icon:
                        key = icon.get('class', [None])[0]
                        val = stat.get_text(strip=True)
                        if key: stats[key] = val

            posts.append({
                'id': tweet_url.split('/')[-1] if tweet_url else None,
                'username': username,
                'text': text,
                'timestamp': timestamp,
                'url': tweet_url.replace('xcancel.com', 'x.com') if tweet_url else None,
                'is_pinned': is_pinned,
                'stats': stats,
                'fetched_at': datetime.now(timezone.utc).isoformat()
            })
            
            if len(posts) >= limit:
                break
                
        log.info(f"Successfully scraped {len(posts)} posts.")
        
    except Exception as e:
        log.error(f"Error scraping @{username}: {e}")
    finally:
        await nav.close()
        
    return posts

def save_posts(username: str, posts: list):
    out_file = DB_DIR / f"x_intel_{username}.json"
    
    # Load existing to avoid duplicates
    existing = []
    if out_file.exists():
        try:
            with open(out_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            existing = []
            
    # Merge based on URL
    existing_urls = {p.get('url') for p in existing if p.get('url')}
    new_filtered = [p for p in posts if p.get('url') not in existing_urls]
    
    merged = new_filtered + existing
    # Keep it clean - sort by timestamp desc if possible
    # (Timestamps are currently strings like 'Apr 12, 2026 · 10:30 PM UTC')
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2)
        
    log.info(f"Saved {len(merged)} total posts to {out_file}")

async def main():
    parser = argparse.ArgumentParser(description='Scrape X posts via XCancel')
    parser.add_argument('--username', required=True, help='X username to scrape')
    parser.add_argument('--limit', type=int, default=20, help='Max posts to scrape')
    args = parser.parse_args()
    
    posts = await fetch_x_posts(args.username, args.limit)
    if posts:
        save_posts(args.username, posts)
        # Also print the latest one
        log.info(f"LATEST POST: {posts[0]['text'][:100]}...")

if __name__ == '__main__':
    asyncio.run(main())
