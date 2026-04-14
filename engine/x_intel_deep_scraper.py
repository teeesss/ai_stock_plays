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

# Verified healthy instances — sorted by points (source: nitter status tracker)
# Session auto-eviction: 2 consecutive failures removes from pool until next run
ALL_MIRRORS = [
    "https://nitter.tiekoetter.com",        # 🇩🇪 42% uptime | 77pts 
    "https://nitter.net",                   # 🇳🇱 94% uptime | 76pts
    "https://nitter.catsarch.com",          # 🇺🇸/🇩🇪 66% uptime | 76pts
    "https://lightbrd.com",                 # 🇹🇷 96% uptime | 75pts
    "https://xcancel.com",                  # 🇺🇸 97% uptime | 72pts 
    "https://nitter.space",                 # 🇺🇸 96% uptime | 71pts 
    "https://nitter.poast.org",             # 🇺🇸 86% uptime | 67pts
    "https://nuku.trabun.org",              # 🇨🇱 95% uptime | 36pts
    "https://nitter.privacyredirect.com",   # 🇫🇮 Let's Encrypt | NSFW
    "https://nitter.us.catsarch.com",       # Subdomain node
    "http://5.78.115.92:8081",              # Direct IP node
    "https://nitter.aishiteiru.moe",
    "https://nitter.aosus.link",
    "https://nitter6.kabii.moe",
    "https://nitter.anoxinon.de",
    "https://nitter.fullex.fr",
    "https://nitter.teamqq.de",
    "https://nitter.thekitten.space",
    "https://nitter.wisq.net",
    "https://nitter.zebes.info",
]

STATE_FILE = DB_DIR / "scraper_state.json"
SCANNED_DAYS_FILE = DB_DIR / "scanned_days.json"


# ─────────────────────────────────────────────────────────────
#  Scanned Days Registry (prevents re-scanning completed days)
# ─────────────────────────────────────────────────────────────
def load_scanned_days(username: str) -> set:
    """Load set of already-scanned date strings (YYYY-MM-DD) for a user."""
    if SCANNED_DAYS_FILE.exists():
        try:
            data = json.loads(SCANNED_DAYS_FILE.read_text(encoding="utf-8"))
            return set(data.get(username, []))
        except Exception:
            pass
    return set()


def mark_day_scanned(username: str, day_str: str):
    """Permanently mark a day as scanned for a user."""
    data = {}
    if SCANNED_DAYS_FILE.exists():
        try:
            data = json.loads(SCANNED_DAYS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    if username not in data:
        data[username] = []
    if day_str not in data[username]:
        data[username].append(day_str)
        SCANNED_DAYS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


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


def reconstruct_tickers(text: str) -> str:
    """V11.0 Surgical Ticker Reconstructor.
    Collapses Nitter fragments but prevents word-smashing.
    """
    if not text:
        return ""

    # 1. Collapse single-letter chains starting with $ ($ N V D A -> $NVDA)
    text = re.sub(r'\$[A-Z](?:\s[A-Z]\b)+', lambda m: m.group(0).replace(" ", ""), text)
    
    # 2. Collapse fragments after a multi-letter ticker ($AA O I -> $AAOI)
    # Matches $ + 2-5 letters + space + sequence of single letters
    text = re.sub(r'\$([A-Z]{2,5})\s([A-Z]\b(?:\s[A-Z]\b)*)', 
                  lambda m: "$" + m.group(1) + m.group(2).replace(" ", ""), text)
    
    # 3. Collapse bare capital chains (C P O -> CPO)
    # Only if starting at a word boundary (prevents smashing into preceding words)
    text = re.sub(r'(?<!\w)[A-Z](?:\s[A-Z]\b)+', lambda m: m.group(0).replace(" ", ""), text)
    
    # 4. Add spaces between smashed tickers ($PGY$NVDA -> $PGY $NVDA)
    text = re.sub(r'(\$[A-Z0-9]{2,10})(\$[A-Z0-9])', r'\1 \2', text)
    
    # 5. Final Spacing Refinement
    text = re.sub(r'([a-z0-9])([\$@])', r'\1 \2', text) # Space before $ or @
    text = re.sub(r'(\$[A-Z0-9]{2,12})([a-z]{2,})', r'\1 \2', text) # $NVDAis -> $NVDA is
    
    return re.sub(r'\s+', ' ', text).strip()


def clean_text_spacing(text: str) -> str:
    """Master formatting pipeline."""
    if not text:
        return ""
    
    # Step 1: Handle handle fragmentation (@Ph o t o n C a p -> @PhotonCap)
    def collapse_fragment(m):
        return m.group(0).replace(" ", "")
    text = re.sub(r'(@[A-Za-z0-9])(?:\s[A-Za-z0-9])+', collapse_fragment, text)

    # Step 2: Safe Reconstruction
    text = reconstruct_tickers(text)
    
    # Step 3: Ensure space AFTER @USER if followed by alphanumeric
    text = re.sub(r'(@[A-Za-z0-9_]{1,20})([a-zA-Z0-9])', r'\1 \2', text)
    
    return re.sub(r'  +', ' ', text).strip()


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
    
    # PHASE 1 FIX: Extract tweet text with cashtag-aware parsing
    # Nitter renders $TICKERS as letter-by-letter spans. We must read each
    # cashtag anchor tag as a single whole unit before stripping HTML.
    
    # Clone the content element to avoid mutating the soup
    content_copy = BeautifulSoup(str(cd), "html.parser")
    
    # Find all cashtag links and replace them with their concatenated text (no separator)
    for cashtag_el in content_copy.select("a.cashtag, a[href*='/search?q=%24']"):
        ticker_text = cashtag_el.get_text(separator="", strip=True)
        cashtag_el.replace_with(f" {ticker_text} ")
    
    # Now get the full text — cashtags are already whole, rest uses space separator
    raw_text = content_copy.get_text(separator=" ", strip=True)
    
    # Clean and reconstruct any remaining broken tickers 
    text = clean_text_spacing(raw_text)
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
    """Scrape a single user's timeline — V9.1 Parallel Smart Cache."""
    user_file = DB_DIR / f"x_intel_{username}.json"

    # Log existing count
    existing_count = 0
    if user_file.exists():
        try:
            raw = json.loads(user_file.read_text(encoding="utf-8"))
            existing_count = len(raw if isinstance(raw, list) else raw.get("posts", []))
        except Exception:
            pass
    log.info(f"Loaded {existing_count} existing posts for @{username}")

    # ── V9.1 SMART GAP FINDER ──────────────────────────────────────────
    # Source A: scanned_days.json sidecar (days searched even if 0 results)
    # Source B: post timestamps in JSON (days that have actual data)
    # Union = done days. Only remaining gaps get scraped.

    scanned = load_scanned_days(username)  # set of 'YYYY-MM-DD' strings

    post_dates = set()
    user_file = DB_DIR / f"x_intel_{username}.json"
    if user_file.exists():
        try:
            raw = json.loads(user_file.read_text(encoding="utf-8"))
            posts_list = raw if isinstance(raw, list) else raw.get("posts", [])
            for p in posts_list:
                ts = p.get("timestamp", "")
                if ts:
                    post_dates.add(ts[:10])
        except Exception:
            pass

    done_days = scanned | post_dates

    start_date = datetime(2025, 10, 1).date()
    end_date   = datetime.now(timezone.utc).date()
    
    # ── V9.2 INTRA-DAY SYNC ───────────────────────────────────────────
    # Force the last 48 hours to always be treated as a gap. This allows
    # the script to be run every few hours — catching live updates while
    # the deduplication safely ignores what was already downloaded today.
    today_str = end_date.strftime("%Y-%m-%d")
    yest_str = (end_date - timedelta(days=1)).strftime("%Y-%m-%d")
    done_days.discard(today_str)
    done_days.discard(yest_str)

    curr = start_date
    gaps = []
    while curr <= end_date:
        if curr.strftime("%Y-%m-%d") not in done_days:
            gaps.append(curr)
        curr += timedelta(days=1)

    if not gaps:
        log.info(f"  ✅ @{username} fully covered — no gaps in forensic window.")
        return []

    log.info(f"--- PARALLEL FORENSIC DRILL V9.1 | @{username} | {len(gaps)} gaps ---")

    # ── MIRROR POOL WITH AUTO-EVICTION ────────────────────────────────
    mirrors = ALL_MIRRORS.copy()
    random.shuffle(mirrors)
    mirror_failures: dict[str, int] = {m: 0 for m in mirrors}  # session-only

    def get_live_mirrors() -> list:
        """Return mirrors that haven't hit 2 consecutive failures this session."""
        live = [m for m in mirrors if mirror_failures.get(m, 0) < 2]
        if not live:
            log.warning("  ⚠️ All mirrors evicted! Resetting pool.")
            for m in mirrors:
                mirror_failures[m] = 0
            live = mirrors[:]
        return live

    # ── QUEUE + WORKERS ───────────────────────────────────────────────
    queue: asyncio.Queue = asyncio.Queue()
    for g in gaps:
        queue.put_nowait(g)

    # Pre-load existing posts for dedup
    existing_list = []
    if user_file.exists():
        try:
            raw = json.loads(user_file.read_text(encoding="utf-8"))
            existing_list = raw if isinstance(raw, list) else raw.get("posts", [])
        except Exception:
            pass

    total_new = [0]
    retry_days: list = []  # days that exhaust all mirrors — rescued after main pass

    async def worker(worker_id: int):
        inst_idx = worker_id
        nav = StealthNavigator(headless=True)
        await nav.initialize()
        try:
            while not queue.empty():
                day = await queue.get()
                s_dt = day.strftime("%Y-%m-%d")
                e_dt = (day + timedelta(days=1)).strftime("%Y-%m-%d")

                success = False
                attempts = 0
                live = get_live_mirrors()

                while not success and attempts < len(live):
                    inst = live[inst_idx % len(live)]
                    h_url = (f"{inst}/search?f=tweets"
                             f"&q=from%3A{username}"
                             f"+since%3A{s_dt}+until%3A{e_dt}")
                    log.info(f"  [W{worker_id}] {s_dt} via {inst}")

                    try:
                        h_posts = await scrape_search_block(nav, h_url, inst, username)

                        if h_posts is None:  # connection/DNS failure
                            mirror_failures[inst] = mirror_failures.get(inst, 0) + 1
                            if mirror_failures[inst] >= 2:
                                log.warning(f"  ⚠️ Evicted {inst} ({mirror_failures[inst]} failures)")
                            inst_idx += 1
                            attempts += 1
                        else:  # success (0 or more posts found)
                            mirror_failures[inst] = 0  # reset on success
                            if h_posts:
                                _incremental_save(username, h_posts, existing_list)
                                # Download images for NEW posts only — disk check
                                await download_images(h_posts, username)
                                # Sync shared list
                                try:
                                    raw2 = json.loads(user_file.read_text(encoding="utf-8"))
                                    new_data = raw2 if isinstance(raw2, list) else raw2.get("posts", [])
                                    existing_list.clear()
                                    existing_list.extend(new_data)
                                except Exception:
                                    pass
                                total_new[0] += len(h_posts)
                            # Mark day done regardless of post count
                            mark_day_scanned(username, s_dt)
                            success = True
                    except Exception as e:
                        log.error(f"  [Worker {worker_id}] Loop Error: {e}")
                        inst_idx += 1
                        attempts += 1
                
                queue.task_done()
                if not success:
                    # Don't mark scanned — day goes to rescue queue
                    log.warning(f"  [W{worker_id}] All mirrors failed for {s_dt} — queued for rescue")
                    retry_days.append(day)
                await asyncio.sleep(random.uniform(10, 18))
        finally:
            await nav.close()

    # ── LAUNCH 4 PARALLEL WORKERS ─────────────────────────────────────
    await asyncio.gather(*[asyncio.create_task(worker(i)) for i in range(4)])

    # ── RESCUE PASS: retry failed days sequentially on proven mirrors ─
    if retry_days:
        log.info(f"  🔁 Rescue pass: {len(retry_days)} days failed all mirrors. Retrying...")
        RESCUE_MIRRORS = [
            "https://xcancel.com",
            "https://nitter.poast.org",
            "https://nitter.tiekoetter.com",
            "https://nitter.net",
            "https://lightbrd.com",
        ]
        nav_rescue = StealthNavigator(headless=True)
        await nav_rescue.initialize()
        try:
            for day in retry_days:
                s_dt = day.strftime("%Y-%m-%d")
                e_dt = (day + timedelta(days=1)).strftime("%Y-%m-%d")
                rescued = False
                for inst in RESCUE_MIRRORS:
                    h_url = (f"{inst}/search?f=tweets"
                             f"&q=from%3A{username}"
                             f"+since%3A{s_dt}+until%3A{e_dt}")
                    log.info(f"  [RESCUE] {s_dt} via {inst}")
                    try:
                        h_posts = await scrape_search_block(nav_rescue, h_url, inst, username)
                        if h_posts is not None:
                            if h_posts:
                                _incremental_save(username, h_posts, existing_list)
                                await download_images(h_posts, username)
                                total_new[0] += len(h_posts)
                            mark_day_scanned(username, s_dt)
                            log.info(f"  [RESCUE] ✅ {s_dt} recovered ({len(h_posts) if h_posts else 0} posts)")
                            rescued = True
                            break
                    except Exception as e:
                        log.warning(f"  [RESCUE] {inst} failed: {e}")
                    await asyncio.sleep(random.uniform(8, 15))
                if not rescued:
                    log.warning(f"  [RESCUE] ❌ {s_dt} still unresolved — will retry next run")
        finally:
            await nav_rescue.close()

    log.info(f"--- PARALLEL DRILL COMPLETE: {total_new[0]} total new for @{username} ---")
    return []

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
        if failures >= 2:
            return None # Signal failure
            
        page = await nav.context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=10000)  # 10s — fast fail
            await asyncio.sleep(random.uniform(2, 5))
            
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
#  Image Downloader (V9.1 — disk-check only, new posts only)
# ─────────────────────────────────────────────────────────────
async def download_images(posts: list, username: str):
    """Download images for the given posts if not already on disk.
    ONLY call with newly-fetched posts — never the full user file.
    Disk presence is the authority: if file exists, skip silently.
    """
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
            rel_path   = f"images/{username}/{local_name}"

            if not local_path.exists():  # ← disk is the truth
                to_download.append((url, local_path, local_name))

            # Keep path recorded in post metadata
            if rel_path not in p.get("images", []):
                p.setdefault("images", []).append(rel_path)

    if not to_download:
        return  # Already downloaded — silent

    log.info(f"  📸 {len(to_download)} new images for @{username}")
    saved = 0
    for url, path, name in to_download:
        try:
            resp = curlr.get(url, impersonate="chrome110", timeout=12)
            if resp.status_code == 200 and len(resp.content) > 500:
                path.write_bytes(resp.content)
                saved += 1
            await asyncio.sleep(random.uniform(0.2, 0.8))
        except Exception as e:
            log.warning(f"  Image fail ({name}): {e}")

    if saved:
        log.info(f"  📸 Saved {saved}/{len(to_download)} images for @{username}")


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
        tickers = re.findall(r"\$([A-Z]{2,12})(?![A-Z])", p.get("text", "").upper())
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
#  Main — SINGLE USER ONLY
# ─────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(
        description="X Intelligence Scraper V9.1 — Single User | Smart Cache | Parallel Mirrors"
    )
    parser.add_argument(
        "--username", type=str, required=True,
        help="Single X handle to scrape. ONE AT A TIME. Example: --username aleabitoreddit"
    )
    parser.add_argument("--days", type=int, default=210)
    parser.add_argument("--instance", type=str, default=None,
                        help="Force a specific mirror instance (optional)")
    args = parser.parse_args()

    user = args.username.strip().lstrip("@")

    log.info(f"{'='*60}")
    log.info(f"X INTEL V9.1 | @{user} | Smart Cache | 4-Worker Parallel")
    log.info(f"{'='*60}")

    await scrape_user(user, max_days=args.days, instance=args.instance)

    # Final dedup pass (already removes duplicates and fixes sort order)
    _deduplicate_file(user)

    # 1. Regex Cleanup (Repairs broken tickers like "$PG Y" -> "$PGY")
    try:
        from repair_tickers import repair_user
        log.info("Running ticker regex cleanup...")
        repair_user(user)
    except ImportError as e:
        log.warning(f"Could not import repair_tickers: {e}")

    # 2. Foreign-to-English Translation Pass
    try:
        from translate_intel import translate
        log.info("Running foreign language translation pass...")
        translate()
    except ImportError as e:
        log.warning(f"Could not import translate_intel: {e}")

    # 3. Rebuild master intel.js bridge
    rebuild_master()

    log.info(f"DONE — @{user} complete. All cleanup scripts executed.")


if __name__ == "__main__":
    asyncio.run(main())
