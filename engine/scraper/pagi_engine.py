import asyncio
import random
import logging
import re
from bs4 import BeautifulSoup

log = logging.getLogger("x_intel.pagi")

async def scrape_pagination_loop(nav, url, inst, username, parse_fn, stop_condition=None):
    """
    Standardized pagination engine for Nitter instances.
    nav: StealthNavigator
    url: Initial URL
    inst: Instance base (e.g. https://nitter.net)
    parse_fn: function(soup_item) -> dict
    stop_condition: function(list_of_posts) -> bool
    """
    all_results = []
    seen_cursors = set()
    failures = 0
    
    while url:
        if failures >= 2:
            log.warning(f"  [PAGI] Max failures reached for @{username} at {url}")
            break
            
        page = await nav.context.new_page()
        try:
            log.info(f"  [PAGI] Fetching: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(random.uniform(2, 5))
            
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            items = soup.select(".timeline-item")
            
            p_count = 0
            page_posts = []
            for item in items:
                p = parse_fn(item, username)
                if p:
                    page_posts.append(p)
                    p_count += 1
            
            all_results.extend(page_posts)
            log.info(f"  [PAGI] Found {p_count} tweets on page.")
            
            if stop_condition and stop_condition(page_posts):
                log.info("  [PAGI] Stop condition met.")
                break
            
            # Extract Next Link
            all_showmore = soup.select(".show-more a")
            next_links = [a for a in all_showmore if "cursor=" in a.get("href", "").lower()]
            showmore = next_links[-1] if next_links else None
            
            if showmore:
                href = showmore.get("href", "")
                cursor_match = re.search(r"cursor=([^&]+)", href)
                new_cursor = cursor_match.group(1) if cursor_match else None
                
                if not new_cursor or new_cursor in seen_cursors:
                    break
                seen_cursors.add(new_cursor)
                url = f"{inst}/search{href}" if href.startswith("?") else f"{inst}{href}"
                failures = 0
            else:
                break
                
        except Exception as e:
            log.warning(f"  [PAGI] Page error: {e}")
            failures += 1
        finally:
            await page.close()
            
    return all_results
