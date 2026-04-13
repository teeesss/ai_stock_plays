"""
engine/x_intel_deep_scraper.py
=============================
Pulls up to 3 months (90 days) of historical posts for specified X users 
via xcancel.com / nitter HTML scraping. Uses StealthNavigator for 
reliable pagination.

Usage: python engine/x_intel_deep_scraper.py --usernames KawzInvests PhotonCap aleabitoreddit --days 90
"""

import os
import json
import logging
import argparse
import asyncio
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from stealth_navigator import StealthNavigator
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from stealth_navigator import StealthNavigator

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'database' / 'x_intel_master.json'

def parse_nitter_date(date_str: str) -> datetime:
    """
    Parses Nitter/XCancel date strings like 'Apr 12, 2026 · 10:30 PM UTC' 
    or '2h ago' or 'Apr 12'.
    """
    now = datetime.now(timezone.utc)
    
    # Handle '2h ago', '5m ago', etc.
    if 'ago' in date_str:
        m = re.search(r'(\d+)([hmd])', date_str)
        if m:
            val, unit = int(m.group(1)), m.group(2)
            if unit == 'h': return now - timedelta(hours=val)
            if unit == 'm': return now - timedelta(minutes=val)
            if unit == 'd': return now - timedelta(days=val)
            
    # Handle 'Apr 12, 2026 · 10:30 PM UTC'
    clean = date_str.split('·')[0].strip()
    try:
        # Try full format
        return datetime.strptime(clean, "%b %d, %Y").replace(tzinfo=timezone.utc)
    except:
        try:
            # Try without year (current year)
            dt = datetime.strptime(clean, "%b %d")
            return dt.replace(year=now.year, tzinfo=timezone.utc)
        except:
            return now

async def scrape_user_history(username: str, max_days: int = 90):
    url = f"https://xcancel.com/{username}"
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_days)
    
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    
    all_posts = []
    seen_ids = set()
    current_url = url
    
    page_count = 1
    while current_url:
        log.info(f"Page {page_count}: Scraping {current_url}")
        
        try:
            page = await nav.context.new_page()
            await page.goto(current_url, wait_until="load", timeout=30000)
            await asyncio.sleep(5) # Wait for content
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            items = soup.select('.timeline-item')
            if not items:
                log.warning(f"No items found on page {page_count}.")
                break
                
            page_oldest_date = datetime.now(timezone.utc)
            
            for item in items:
                content_div = item.select_one('.tweet-content')
                date_link = item.select_one('.tweet-date a')
                if not content_div or not date_link: continue
                
                tweet_id = date_link.get('href').split('/')[-1].split('#')[0]
                if tweet_id in seen_ids: continue
                
                raw_date = date_link.get('title', '')
                dt = parse_nitter_date(raw_date)
                page_oldest_date = min(page_oldest_date, dt)
                
                text = content_div.get_text(strip=True)
                
                post = {
                    'id': tweet_id,
                    'username': username,
                    'text': text,
                    'timestamp': dt.isoformat(),
                    'raw_date': raw_date,
                    'url': f"https://x.com/{username}/status/{tweet_id}",
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                }
                
                all_posts.append(post)
                seen_ids.add(tweet_id)
            
            log.info(f"Page {page_count} complete. Total posts so far: {len(all_posts)}. Oldest on page: {page_oldest_date.date()}")
            
            # Check if we should continue
            if page_oldest_date < cutoff_date:
                log.info(f"Reached cutoff date {cutoff_date.date()}. Stopping.")
                break
                
            # Find 'More' button
            more_btn = soup.select_one('.show-more a')
            if more_btn:
                current_url = f"https://xcancel.com{more_btn.get('href')}"
                page_count += 1
                await page.close()
            else:
                log.info("No more pages found.")
                break
                
        except Exception as e:
            log.error(f"Error on page {page_count}: {e}")
            break
            
    await nav.close()
    return all_posts

def save_master(posts: list):
    master_data = []
    if DB_PATH.exists():
        try:
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
        except: pass
        
    seen_ids = {p['id'] for p in master_data if 'id' in p}
    new_filtered = [p for p in posts if p['id'] not in seen_ids]
    
    combined = new_filtered + master_data
    # Sort by date desc
    combined.sort(key=lambda x: x['timestamp'], reverse=True)
    
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2)
    
    # Save as JS for dashboard
    js_path = DB_PATH.with_suffix('.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('// GIGACPO Intelligence Data - Auto-generated\n')
        f.write('window.X_INTEL = ')
        json.dump(combined, f)
        f.write(';')
        
    log.info(f"Master intelligence updated. Total posts: {len(combined)} ({len(new_filtered)} new).")
    log.info(f"Exported to {js_path}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--usernames', nargs='+', default=['KawzInvests', 'PhotonCap', 'aleabitoreddit'])
    parser.add_argument('--days', type=int, default=90)
    args = parser.parse_args()
    
    all_new_posts = []
    for user in args.usernames:
        posts = await scrape_user_history(user, max_days=args.days)
        all_new_posts.extend(posts)
        
    if all_new_posts:
        save_master(all_new_posts)

if __name__ == '__main__':
    asyncio.run(main())
