"""
X Intelligence Deep Scraper V8 — Playwright-Only, Crash-Resilient
=================================================================
PROVEN: curl_cffi gets ZERO tweets (JS anti-bot blocks it).
PROVEN: Playwright gets 20 tweets/page consistently.
PROVEN: nitter.tiekoetter.com allows 5+ pages with 10-15s delays.
PROVEN: Cursors are instance-specific — NEVER rotate mid-session.

Strategy:
  - Playwright headless browser (StealthNavigator)
  - Stick to ONE instance per user session  
  - Save after EVERY page (crash resilience)
  - State file tracks cursor so we can resume after interruption
  - Loop Detection: Track last 10 cursors to prevent pagination loops
  - Stale Detection: Stop if 3 consecutive pages yield 0 new/unseen posts
  - Images downloaded into subfolders: images/<username>/
"""
import asyncio
import json
import re
import random
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup

import sys
sys.path.append(str(Path(__file__).parent))
from stealth_navigator import StealthNavigator

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("x_intel")

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"
IMG_DIR = ROOT / "images"
IMG_DIR.mkdir(exist_ok=True)

# Only instances proven to work with Playwright
LIVE_INSTANCES = [
    "https://nitter.tiekoetter.com",
    "https://xcancel.com",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org"
]

STATE_FILE = DB_DIR / "scraper_state.json"


# ─────────────────────────────────────────────────────────────
#  Date Parsing
# ─────────────────────────────────────────────────────────────
def parse_date(raw: str) -> datetime:
    """
    Parses nitter date strings like:
    - 'Apr 13, 2026 · 12:36 AM UTC'
    - '5h'
    - '20m'
    - 'Jan 1'
    """
    now = datetime.now(timezone.utc)
    try:
        if not raw:
            return now
            
        if "·" in raw:
            clean = raw.split("·")[0].strip()
            # Handles "Apr 13, 2026"
            return datetime.strptime(clean, "%b %d, %Y").replace(tzinfo=timezone.utc)
        
        raw = raw.strip().lower()
        
        # Relative: "5h", "20m", "1s"
        if raw.endswith("h"):
            try:
                v = int(raw[:-1])
                return now - timedelta(hours=v)
            except: return now
        if raw.endswith("m"):
            try:
                v = int(raw[:-1])
                return now - timedelta(minutes=v)
            except: return now
        if raw.endswith("s"):
            return now
            
        # Shorthand: "Jan 1"
        parts = raw.split()
        if len(parts) == 2:
            dt = datetime.strptime(f"{raw}, {now.year}", "%b %d, %Y")
            return dt.replace(tzinfo=timezone.utc)
             
        return now
    except Exception:
        return now


def clean_text_spacing(text: str) -> str:
    """Ensures $TICKERS and @USERNAMES have spaces around them for readability."""
    if not text:
        return ""
    
    # 1. Ensure space BEFORE $ or @ if preceded by alphanumeric
    text = re.sub(r'([a-zA-Z0-9])([\$@])', r'\1 \2', text)
    
    # 2. Ensure space AFTER $TICKER (uppercase) if followed by alphanumeric
    text = re.sub(r'(\$[A-Z]{2,10})([a-zA-Z0-9])', r'\1 \2', text)
    
    # 3. Ensure space AFTER $ticker (lowercase) if followed by alphanumeric
    text = re.sub(r'(\$[a-z]{2,10})([a-zA-Z0-9])', r'\1 \2', text)
    
    # 4. Ensure space AFTER @USER if followed by alphanumeric
    text = re.sub(r'(@[A-Za-z0-9_]{1,20})([a-zA-Z0-9])', r'\1 \2', text)
    
    return text


def garbage_purge(text: str) -> bool:
    """Returns True if text is garbage or system error."""
    if not text or len(text.strip()) < 2:
        return True
    lower = text.lower().strip()
    if lower in ["whoops", "whoops...", "fetching..."] or "nitter has been blocked" in lower:
        return True
    return False


def parse_tweet(item, username: str) -> dict:
    """Parses a single nitter timeline item into a standard dict."""
    cd = item.select_one(".tweet-content")
    dl = item.select_one(".tweet-date a")
    if not cd or not dl:
        return None
    
    # Skip pinned
    if item.select_one(".pinned"):
        return None
        
    tweet_id = dl.get("href", "").split("/")[-1].split("#")[0]
    raw_date = dl.get("title", "")
    ts_dt = parse_date(raw_date)
    
    # Clean text
    text = clean_text_spacing(cd.get_text(separator=" ", strip=True))
    if garbage_purge(text):
        return None

    # Images
    imgs = item.select(".attachments img")
    img_urls = []
    local_paths = []
    for i, img in enumerate(imgs):
        src = img.get("src", "")
        if src:
            if src.startswith("/"):
                 src = f"https://xcancel.com{src}" 
            img_urls.append(src)
            local_paths.append(f"images/{username}/{tweet_id}_{i}.jpg")
            
    return {
        "id": tweet_id,
        "username": username,
        "text": text,
        "timestamp": ts_dt.isoformat(),
        "_timestamp_dt": ts_dt, # helper for internal cutoff checks
        "raw_date": raw_date,
        "images": local_paths,
        "image_urls": img_urls,
        "url": f"https://x.com/{username}/status/{tweet_id}",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────
#  State Persistence (resume after crash / interruption)
# ─────────────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────
#  Core Scraper
# ─────────────────────────────────────────────────────────────
async def scrape_user(username: str, max_days: int = 210, instance: str = None):
    """Scrape a single user's timeline using Playwright. Returns new posts."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    
    inst_pool = list(LIVE_INSTANCES)
    if instance and instance in inst_pool:
        inst_pool.remove(instance)
        inst_pool.insert(0, instance)
    
    inst_idx = 0
    inst = inst_pool[inst_idx]

    # Load existing posts to deduplicate
    user_file = DB_DIR / f"x_intel_{username}.json"
    existing = []
    seen_ids = set()
    if user_file.exists():
        try:
            existing = json.loads(user_file.read_text(encoding="utf-8"))
            seen_ids = {p["id"] for p in existing if "id" in p}
            log.info(f"Loaded {len(seen_ids)} existing posts for @{username}")
        except Exception:
            pass

    # Check for resume state
    state = load_state()
    user_state = state.get(username, {})
    resume_cursor = user_state.get("cursor")
    oldest_date_iso = user_state.get("oldest_date")
    is_search = user_state.get("is_search_fallback", False)
    
    if is_search and oldest_date_iso and resume_cursor:
        old_dt = datetime.fromisoformat(oldest_date_iso).strftime('%Y-%m-%d')
        since_dt = (datetime.fromisoformat(oldest_date_iso) - timedelta(days=30)).strftime('%Y-%m-%d')
        url = f"{inst}/search?f=tweets&q=from%3A{username}+since%3A{since_dt}+until%3A{old_dt}&cursor={resume_cursor}"
        log.info(f"RESUMING @{username} from SEARCH FALLBACK cursor")
    elif resume_cursor:
        url = f"{inst}/{username}?cursor={resume_cursor}"
        log.info(f"RESUMING @{username} from saved cursor")
    elif oldest_date_iso:
        old_dt = datetime.fromisoformat(oldest_date_iso).strftime('%Y-%m-%d')
        since_dt = (datetime.fromisoformat(oldest_date_iso) - timedelta(days=30)).strftime('%Y-%m-%d')
        url = f"{inst}/search?f=tweets&q=from%3A{username}+since%3A{since_dt}+until%3A{old_dt}"
        log.info(f"RESUMING @{username} from SEARCH FALLBACK (until {old_dt})")
    else:
        url = f"{inst}/{username}"

    # Launch browser
    nav = StealthNavigator(headless=True)
    await nav.initialize()

    new_posts = []
    page_num = 0
    failures = 0
    absolute_failures = 0
    stale_pages = 0
    seen_cursors = set()
    if resume_cursor:
        seen_cursors.add(resume_cursor)
        
    page_oldest = datetime.now(timezone.utc)
    if oldest_date_iso:
        page_oldest = datetime.fromisoformat(oldest_date_iso)

    # NEW: If we are deep backfilling, use FORWARD HARVEST starting from the cutoff
    if page_oldest > cutoff + timedelta(days=1): # We haven't reached the cutoff yet
        log.info(f"--- FORWARD HARVEST MODE ENGAGED for @{username} ---")
        current_start = cutoff
        while current_start < datetime.now(timezone.utc):
            current_end = current_start + timedelta(days=33)
            if current_end > datetime.now(timezone.utc):
                current_end = datetime.now(timezone.utc)
            
            s_dt = current_start.strftime('%Y-%m-%d')
            e_dt = current_end.strftime('%Y-%m-%d')
            
            # Skip if we already have data in this window? 
            # Actually, forward harvest is for FILLING GAPS.
            h_url = f"{inst}/search?f=tweets&q=from%3A{username}+since%3A{s_dt}+until%3A{e_dt}"
            log.info(f"  Harvesting block: {s_dt} to {e_dt}")
            
            h_posts = await scrape_search_block(nav, h_url, inst, username)
            if h_posts:
                _incremental_save(username, h_posts, existing)
                # Reload existing so we don't save duplicates in next block
                existing = json.loads(user_file.read_text(encoding="utf-8"))
            
            current_start = current_end
            await asyncio.sleep(random.uniform(5, 10))
            
        log.info(f"--- HARVEST COMPLETE for @{username} ---")
        return [] # We've already saved everything
    
    try:
        while url:
            if absolute_failures >= 12:
                log.error(f"  ABORTING: Hit 12 absolute failures across multiple instances. Complete IP/network block.")
                break

            if failures >= 3:
                inst_idx = (inst_idx + 1) % len(inst_pool)
                inst = inst_pool[inst_idx]
                log.warning(f"  Too many failures. Rotating instance to: {inst} and switching to SEARCH FALLBACK.")
                failures = 0
                
                # We CANNOT carry cursors across instances. Must use Search Fallback securely.
                old_dt = page_oldest.strftime('%Y-%m-%d')
                since_dt = (page_oldest - timedelta(days=30)).strftime('%Y-%m-%d')
                url = f"{inst}/search?f=tweets&q=from%3A{username}+since%3A{since_dt}+until%3A{old_dt}"
                
                # Clear cursor since we're pivoting
                state[username] = state.get(username, {})
                state[username].pop("cursor", None)
                save_state(state)
                continue

            page_num += 1
            log.info(f"Page {page_num}: {url[:90]}...")

            page = await nav.context.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                wait = random.uniform(7, 12)
                await asyncio.sleep(wait)

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                items = soup.select(".timeline-item")
                tweets = soup.select(".tweet-content")

                if not tweets:
                    log.warning(f"  Page {page_num}: 0 tweets — possible block or empty page")
                    
                    if "search" in url:
                        # Gap sliding: ONLY slide if we hit 0 on the FIRST page of a search window.
                        # If we already found tweets in this window, it's a pagination fail, not an empty window.
                        if page_new_this_session == 0:
                            page_oldest = page_oldest - timedelta(days=30)
                            if page_oldest < cutoff:
                                log.info(f"  Search window slid past cutoff. Done @{username}.")
                                break
                            
                            old_dt = page_oldest.strftime('%Y-%m-%d')
                            since_dt = (page_oldest - timedelta(days=30)).strftime('%Y-%m-%d')
                            url = f"{inst}/search?f=tweets&q=from%3A{username}+since%3A{since_dt}+until%3A{old_dt}"
                            log.info(f"  🔀 Window empty. Sliding search window back: {since_dt} to {old_dt}")
                            await page.close()
                            continue
                        else:
                            log.warning(f"  Search pagination failed mid-window. Triggering rotation.")
                            failures += 1
                            absolute_failures += 1
                    else:
                        failures += 1
                        absolute_failures += 1
                    await page.close()
                    await asyncio.sleep(random.uniform(15, 30))
                    continue

                failures = 0  # reset on success
                absolute_failures = 0
                page_new_this_session = 0
                page_truly_new = 0 # Not even in existing file

                for item in items:
                    post = parse_tweet(item, username)
                    if not post:
                        continue
                    
                    tweet_id = post["id"]
                    ts_dt = post["_timestamp_dt"]
                    
                    if tweet_id in seen_ids:
                        continue
                        
                    if ts_dt < page_oldest:
                        page_oldest = ts_dt
                    
                    new_posts.append(post)
                    seen_ids.add(tweet_id)
                    page_new_this_session += 1
                    
                    # Check if truly new (not in existing list)
                    existing_ids = {p["id"] for p in existing}
                    if tweet_id not in existing_ids:
                        page_truly_new += 1

                log.info(
                    f"  Page {page_num}: {len(tweets)} tweets, {page_new_this_session} session-new, {page_truly_new} total-new. "
                    f"Oldest: {page_oldest.strftime('%b %d, %Y')}. "
                    f"Running total: {len(new_posts)}"
                )

                # Loop detection: If we see NO new posts at all for 3 pages, Nitter might be looping
                if page_new_this_session == 0:
                    stale_pages += 1
                    if stale_pages >= 3:
                        log.warning(f"  Detected {stale_pages} stale pages (0 new tweets). Triggering SEARCH FALLBACK.")
                        stale_pages = 0
                        old_dt = page_oldest.strftime('%Y-%m-%d')
                        since_dt = (page_oldest - timedelta(days=30)).strftime('%Y-%m-%d')
                        url = f"{inst}/search?f=tweets&q=from%3A{username}+since%3A{since_dt}+until%3A{old_dt}"
                        
                        # Wipe cursor so we resume from oldest_date natively
                        state[username] = state.get(username, {})
                        state[username].pop("cursor", None)
                        save_state(state)
                        await page.close()
                        continue
                else:
                    stale_pages = 0

                # Check cutoff
                if page_oldest < cutoff:
                    log.info(f"  Reached {max_days}-day cutoff. Done with @{username}.")
                    # Clear resume state
                    state.pop(username, None)
                    save_state(state)
                    await page.close()
                    break

                # Get next cursor — MUST use the one with 'cursor='
                # Page 1 has 1 button (bottom "Load more")
                # Page 2+ has 2 buttons: top "Load newest" + bottom "Load more"
                # "Load newest" usually points to /username without a cursor.
                all_showmore = soup.select(".show-more a")
                next_links = [a for a in all_showmore if "cursor=" in a.get("href", "").lower()]
                
                showmore = next_links[-1] if next_links else None
                
                if showmore:
                    href = showmore.get("href", "")
                    cursor_match = re.search(r"cursor=([^&]+)", href)
                    new_cursor = cursor_match.group(1) if cursor_match else None
                    
                    # Prevent infinite loop or reset to top
                    if not new_cursor or new_cursor in seen_cursors:
                        log.warning(f"  Cursor loop detected or empty cursor. Triggering SEARCH FALLBACK.")
                        old_dt = page_oldest.strftime('%Y-%m-%d')
                        since_dt = (page_oldest - timedelta(days=30)).strftime('%Y-%m-%d')
                        url = f"{inst}/search?f=tweets&q=from%3A{username}+since%3A{since_dt}+until%3A{old_dt}"
                        
                        state[username] = state.get(username, {})
                        state[username].pop("cursor", None)
                        save_state(state)
                        await page.close()
                        continue
                    
                    seen_cursors.add(new_cursor)

                    if href.startswith("?"):
                        if "search" in url:
                            url = f"{inst}/search{href}"
                        else:
                            url = f"{inst}/{username}{href}"
                    else:
                        url = f"{inst}{href}"

                    # Save cursor state for crash recovery
                    state[username] = {
                        "cursor": new_cursor,
                        "page": page_num,
                        "posts_so_far": len(new_posts),
                        "oldest_date": page_oldest.isoformat(),
                        "is_search_fallback": "search" in url,
                        "instance": inst,
                        "updated": datetime.now(timezone.utc).isoformat()
                    }
                    save_state(state)
                    log.info(f"  Saved state for @{username} at page {page_num}")
                else:
                    log.info(f"  No 'Load more' button found. End of history for @{username}.")
                    state.pop(username, None)
                    save_state(state)
                    break

            except Exception as e:
                log.error(f"  Page {page_num} error: {e}")
                failures += 1
            finally:
                try:
                    await page.close()
                except Exception:
                    pass

            # ── SAVE AFTER EVERY PAGE (crash resilience) ──
            if new_posts:
                _incremental_save(username, new_posts, existing)

            # Stealth delay
            delay = random.uniform(12, 20)
            log.info(f"  Sleeping {delay:.0f}s...")
            await asyncio.sleep(delay)

    finally:
        await nav.close()

    return new_posts


# ─────────────────────────────────────────────────────────────
#  Incremental Save (after every page)
# ─────────────────────────────────────────────────────────────
def _incremental_save(username: str, new_posts: list, existing: list):
    """Save user file after each page so nothing is lost on crash."""
    existing_ids = {p["id"] for p in existing}
    
    # Strip internal helpers before saving
    clean_new = []
    for p in new_posts:
        p_clean = p.copy()
        p_clean.pop("_timestamp_dt", None)
        clean_new.append(p_clean)

    truly_new = [p for p in clean_new if p["id"] not in existing_ids]
    if not truly_new:
        return
     
    combined = truly_new + existing
    combined.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    user_file = DB_DIR / f"x_intel_{username}.json"
    user_file.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info(f"  💾 Saved {len(combined)} posts for @{username} ({len(truly_new)} new)")


async def scrape_search_block(nav, url, inst, username):
    """Scrapes a single search block with simple pagination."""
    block_posts = []
    seen_cursors = set()
    failures = 0
    
    while url:
        if failures >= 3:
            break
            
        page = await nav.context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(random.uniform(5, 8))
            
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            items = soup.select(".timeline-item")
            
            p_count = 0
            for item in items:
                p = parse_tweet(item, username)
                if p and not garbage_purge(p["text"]):
                    block_posts.append(p)
                    p_count += 1
            
            log.info(f"    Block Page: Found {p_count} tweets.")
            
            # Next cursor
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
            log.warning(f"    Block error: {e}")
            failures += 1
        finally:
            await page.close()
            
    return block_posts


def _deduplicate_file(username: str):
    """Deep cleanup and deduplication of a user's JSON file."""
    user_file = DB_DIR / f"x_intel_{username}.json"
    if not user_file.exists():
        return
    
    try:
        posts = json.loads(user_file.read_text(encoding="utf-8"))
        seen = set()
        deduped = []
        for p in posts:
            if p["id"] not in seen:
                # Re-clean spacing
                p["text"] = clean_text_spacing(p.get("text", ""))
                
                # GARBAGE PURGE
                if garbage_purge(p["text"]):
                    continue
                    
                deduped.append(p)
                seen.add(p["id"])
        
        deduped.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        user_file.write_text(json.dumps(deduped, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info(f"  ✨ Deduplicated & Purged @{username}: {len(posts)} -> {len(deduped)} posts.")
    except Exception as e:
        log.error(f"  Failed to deduplicate @{username}: {e}")


# ─────────────────────────────────────────────────────────────
#  Image Downloader
# ─────────────────────────────────────────────────────────────
async def download_images(posts: list, username: str):
    """Download images into user-specific folders using curl_cffi."""
    try:
        from curl_cffi import requests as curlr
    except ImportError:
        log.warning("curl_cffi not available — skipping image downloads")
        return

    user_img_dir = IMG_DIR / username
    user_img_dir.mkdir(parents=True, exist_ok=True)

    to_download = []
    for p in posts:
        for i, url in enumerate(p.get("image_urls", [])):
            local_name = f"{p['id']}_{i}.jpg"
            local_path = user_img_dir / local_name
            
            # Map path for JSON
            rel_path = f"images/{username}/{local_name}"
            
            if not local_path.exists():
                to_download.append((url, local_path, local_name))
            
            # Ensure path is in 'images' list
            if rel_path not in p.get("images", []):
                p.setdefault("images", []).append(rel_path)

    if not to_download:
        log.info(f"All images for @{username} already downloaded.")
        return

    log.info(f"Downloading {len(to_download)} images for @{username}...")
    downloaded = 0
    for url, path, name in to_download:
        try:
            resp = curlr.get(url, impersonate="chrome110", timeout=15)
            if resp.status_code == 200 and len(resp.content) > 500:
                path.write_bytes(resp.content)
                downloaded += 1
            await asyncio.sleep(random.uniform(0.5, 2))
        except Exception as e:
            log.warning(f"  Image failed ({name}): {e}")

    log.info(f"Downloaded {downloaded}/{len(to_download)} images for @{username}.")


# ─────────────────────────────────────────────────────────────
#  Master Database Builder
# ─────────────────────────────────────────────────────────────
def rebuild_master():
    """Rebuild master database from all per-user files."""
    all_posts = []
    for f in DB_DIR.glob("x_intel_*.json"):
        if f.name == "x_intel_master.json":
            continue
        try:
            posts = json.loads(f.read_text(encoding="utf-8"))
            all_posts.extend(posts)
        except Exception:
            pass

    all_posts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Deduplicate by ID
    seen = set()
    deduped = []
    for p in all_posts:
        if p["id"] not in seen:
            deduped.append(p)
            seen.add(p["id"])
    all_posts = deduped

    # Compute buzz
    now = datetime.now(timezone.utc)
    periods = {
        "24h": now - timedelta(days=1),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30),
    }
    buzz = {}
    for p in all_posts:
        try:
            dt = datetime.fromisoformat(p["timestamp"])
        except Exception:
            continue
        tickers = re.findall(r"\$([A-Z]{2,5})(?![A-Z])", p.get("text", "").upper())
        for t in set(tickers):
            if t not in buzz:
                buzz[t] = {"24h": 0, "7d": 0, "30d": 0, "total": 0}
            buzz[t]["total"] += 1
            for k, cutoff in periods.items():
                if dt > cutoff:
                    buzz[t][k] += 1

    payload = {
        "posts": all_posts,
        "buzz": buzz,
        "last_updated": now.isoformat(),
    }

    # Save master JSON
    master_path = DB_DIR / "x_intel_master.json"
    master_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Save intel.js for dashboard (both locations)
    js_content = "window.X_INTEL_MODULE = " + json.dumps(payload) + ";"
    (DB_DIR / "intel.js").write_text(js_content, encoding="utf-8")
    (ROOT / "intel.js").write_text(js_content, encoding="utf-8")

    log.info(f"Master rebuilt: {len(all_posts)} posts, {len(buzz)} tickers")
    return payload


# ─────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="X Intelligence Scraper V8")
    parser.add_argument(
        "--usernames", nargs="+",
        default=["KawzInvests", "PhotonCap", "aleabitoreddit"],
    )
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--instance", type=str, default=None)
    parser.add_argument("--no-images", action="store_true")
    args = parser.parse_args()

    usernames = []
    for u in args.usernames:
        if "," in u:
            usernames.extend([x.strip() for x in u.split(",") if x.strip()])
        else:
            usernames.append(u.strip())

    for i, user in enumerate(usernames):
        log.info(f"{'='*60}")
        log.info(f"SCRAPING @{user} ({i+1}/{len(usernames)}) — {args.days} days")
        log.info(f"{'='*60}")

        inst = args.instance or LIVE_INSTANCES[i % len(LIVE_INSTANCES)]
        posts = await scrape_user(user, max_days=args.days, instance=inst)

        if not args.no_images:
            # We call download_images on ALL posts in the user file to ensure backfill
            user_file = DB_DIR / f"x_intel_{user}.json"
            if user_file.exists():
                all_current_posts = json.loads(user_file.read_text(encoding="utf-8"))
                await download_images(all_current_posts, user)
                
                # Re-save with local image paths updated
                user_file.write_text(json.dumps(all_current_posts, indent=2, ensure_ascii=False), encoding="utf-8")
            
            # Final deduplication pass
            _deduplicate_file(user)

        if i < len(args.usernames) - 1:
            pause = random.uniform(30, 60)
            log.info(f"Pausing {pause:.0f}s before next user...")
            await asyncio.sleep(pause)

    # Rebuild master database from all user files
    rebuild_master()
    log.info("DONE.")


if __name__ == "__main__":
    asyncio.run(main())
