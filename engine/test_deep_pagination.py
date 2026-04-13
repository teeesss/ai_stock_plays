"""Test: Can Playwright deep-paginate? This is THE critical test.
Tests 5 pages with proper delays to see if we get blocked."""
import asyncio, json, random, time
from pathlib import Path
from datetime import datetime, timezone
import sys
sys.path.append(str(Path(__file__).parent))
from stealth_navigator import StealthNavigator
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent.parent
INSTANCES = [
    "https://xcancel.com",
    "https://nitter.tiekoetter.com",
]

async def deep_page_test(username="KawzInvests", max_pages=5):
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    
    all_posts = []
    inst_idx = 0
    inst = INSTANCES[inst_idx]
    url = f"{inst}/{username}"
    
    for page_num in range(1, max_pages + 1):
        print(f"\n--- PAGE {page_num} ---")
        print(f"URL: {url}")
        
        page = await nav.context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # Human-like wait
            wait = random.uniform(6, 12)
            print(f"  Waiting {wait:.1f}s for render...")
            await asyncio.sleep(wait)
            
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            tweets = soup.select(".tweet-content")
            dates = soup.select(".tweet-date a")
            showmore = soup.select(".show-more a")
            
            if not tweets:
                print(f"  NO TWEETS on page {page_num}! Trying Playwright click approach...")
                # Maybe the page loaded but needs JS interaction
                # Check for error messages
                error_text = soup.get_text()[:200]
                print(f"  Page text: {error_text}")
                
                # Try rotating instance
                inst_idx = (inst_idx + 1) % len(INSTANCES)
                inst = INSTANCES[inst_idx]
                # Rebuild URL with same cursor
                import re
                m = re.search(r'cursor=[^&]+', url)
                cursor_param = m.group(0) if m else ""
                url = f"{inst}/{username}?{cursor_param}" if cursor_param else f"{inst}/{username}"
                print(f"  Rotated to {inst}, retrying...")
                await page.close()
                await asyncio.sleep(random.uniform(15, 25))
                continue
            
            print(f"  Tweets: {len(tweets)}, Dates: {len(dates)}, Pagination: {bool(showmore)}")
            
            # Extract posts
            items = soup.select(".timeline-item")
            page_oldest = None
            for item in items:
                cd = item.select_one(".tweet-content")
                dl = item.select_one(".tweet-date a")
                if not cd or not dl:
                    continue
                href = dl.get("href", "")
                tweet_id = href.split("/")[-1].split("#")[0]
                raw_date = dl.get("title", "")
                text = cd.get_text(strip=True)
                
                post = {
                    "id": tweet_id,
                    "username": username,
                    "text": text[:120],
                    "raw_date": raw_date,
                }
                all_posts.append(post)
                page_oldest = raw_date
            
            print(f"  Oldest date on page: {page_oldest}")
            print(f"  Running total: {len(all_posts)} posts")
            
            # Get next page URL
            if showmore:
                href = showmore[0].get("href", "")
                # ROTATE INSTANCE per page for stealth
                inst_idx = (inst_idx + 1) % len(INSTANCES)
                inst = INSTANCES[inst_idx]
                if href.startswith("?"):
                    url = f"{inst}/{username}{href}"
                else:
                    url = f"{inst}{href}"
                print(f"  Next page via {inst}")
            else:
                print("  No more pages!")
                break
                
        except Exception as e:
            print(f"  ERROR: {e}")
            break
        finally:
            await page.close()
        
        # Stealth delay between pages
        delay = random.uniform(12, 20)
        print(f"  Sleeping {delay:.1f}s before next page...")
        await asyncio.sleep(delay)
    
    await nav.close()
    
    print(f"\n{'='*60}")
    print(f"DEEP PAGINATION RESULT: {len(all_posts)} total posts across {min(page_num, max_pages)} pages")
    if all_posts:
        print(f"First post: {all_posts[0]['raw_date']}")
        print(f"Last post:  {all_posts[-1]['raw_date']}")
    print(f"{'='*60}")
    
    return all_posts

posts = asyncio.run(deep_page_test())
