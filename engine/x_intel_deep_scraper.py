"""
X Intelligence Deep Scraper V8 - Playwright-Only, Crash-Resilient
=================================================================
PROVEN: curl_cffi gets ZERO tweets (JS anti-bot blocks it).
PROVEN: Playwright gets 20 tweets/page consistently.
PROVEN: nitter.tiekoetter.com allows 5+ pages with 10-15s delays.
PROVEN: Cursors are instance-specific - NEVER rotate mid-session.

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
try:
    from vx_rescue_fetcher import rescue_tweet
except ImportError:
    from engine.vx_rescue_fetcher import rescue_tweet

from bs4 import BeautifulSoup

import sys
sys.path.append(str(Path(__file__).parent))
from stealth_navigator import StealthNavigator

# V16.2 Refactor: Modular Domain Logic
from scraper.dom_parser import parse_tweet, garbage_purge, clean_text_spacing
from scraper.pagi_engine import scrape_pagination_loop

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"
IMG_DIR = ROOT / "images"
IMG_DIR.mkdir(exist_ok=True)
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"{Path(__file__).stem}.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("x_intel")

# Verified healthy instances - sorted by points (source: nitter status tracker)
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
# DOM Parsing and Date Logic moved to engine/scraper/dom_parser.py 
# (V16.2 Refactor for technical hygiene)


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
async def scrape_user(username: str, max_days: int = 210, instance: str = None, since: str = None, until: str = None, search_query: str = ""):
    """Scrape a single user's timeline - V9.2 Advanced Filtering."""
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
    # the script to be run every few hours - catching live updates while
    # the deduplication safely ignores what was already downloaded today.
    today_str = end_date.strftime("%Y-%m-%d")
    yest_str = (end_date - timedelta(days=1)).strftime("%Y-%m-%d")
    done_days.discard(today_str)
    done_days.discard(yest_str)

    if since and until:
        gaps = []
        curr = datetime.strptime(since, "%Y-%m-%d").date()
        target_end = datetime.strptime(until, "%Y-%m-%d").date()
        while curr <= target_end:
            gaps.append(curr)
            curr += timedelta(days=1)
        log.info(f"  [TARGET] Manual Range: {since} to {until} ({len(gaps)} days)")
    else:
        curr = start_date
        gaps = []
        while curr <= end_date:
            if curr.strftime("%Y-%m-%d") not in done_days:
                gaps.append(curr)
            curr += timedelta(days=1)

    if not gaps:
        log.info(f"  [OK] @{username} fully covered - no gaps in forensic window.")
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
            log.warning("  All mirrors evicted! Resetting pool.")
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
    retry_days: list = []  # days that exhaust all mirrors - rescued after main pass

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
                    query_part = f"from%3A{username}"
                    if search_query:
                        query_part += f"%20{search_query.replace(' ', '%20')}"
                    
                    h_url = (f"{inst}/search?f=tweets"
                             f"&q={query_part}"
                             f"%20since%3A{s_dt}%20until%3A{e_dt}")
                    log.info(f"  [W{worker_id}] {s_dt} via {inst}")

                    try:
                        h_posts = await scrape_search_block(nav, h_url, inst, username)

                        if h_posts is None:  # connection/DNS failure
                            mirror_failures[inst] = mirror_failures.get(inst, 0) + 1
                            if mirror_failures[inst] >= 2:
                                log.warning(f"  [WARN] Evicted {inst} ({mirror_failures[inst]} failures)")
                            inst_idx += 1
                            attempts += 1
                        else:  # success (0 or more posts found)
                            mirror_failures[inst] = 0  # reset on success
                            if h_posts:
                                # VX RESCUE: If nitter returns empty or short posts, attempt repair
                                rescued_posts = []
                                for p in h_posts:
                                    # If text is truncated (ends in ...) or is very short, try VX
                                    if p.get("text", "").endswith("...") or len(p.get("text", "")) < 20:
                                        p = rescue_tweet(p)
                                    rescued_posts.append(p)
                                
                                _incremental_save(username, rescued_posts, existing_list)
                                # Download images for NEW posts only - disk check
                                await download_images(rescued_posts, username)
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
                    # Don't mark scanned - day goes to rescue queue
                    log.warning(f"  [W{worker_id}] All mirrors failed for {s_dt} - queued for rescue")
                    retry_days.append(day)
                await asyncio.sleep(random.uniform(10, 18))
        finally:
            await nav.close()

    # ── LAUNCH 4 PARALLEL WORKERS ─────────────────────────────────────
    await asyncio.gather(*[asyncio.create_task(worker(i)) for i in range(4)])

    # ── RESCUE PASS: retry failed days sequentially on proven mirrors ─
    if retry_days:
        log.info(f"  Rescue pass: {len(retry_days)} days failed all mirrors. Retrying...")
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
                    query_part = f"from%3A{username}"
                    if search_query:
                        query_part += f"%20{search_query.replace(' ', '%20')}"
                    
                    h_url = (f"{inst}/search?f=tweets"
                             f"&q={query_part}"
                             f"%20since%3A{s_dt}%20until%3A{e_dt}")
                    log.info(f"  [RESCUE] {s_dt} via {inst}")
                    try:
                        h_posts = await scrape_search_block(nav_rescue, h_url, inst, username)
                        if h_posts is not None:
                            if h_posts:
                                _incremental_save(username, h_posts, existing_list)
                                await download_images(h_posts, username)
                                total_new[0] += len(h_posts)
                            mark_day_scanned(username, s_dt)
                            log.info(f"  [RESCUE] OK {s_dt} recovered ({len(h_posts) if h_posts else 0} posts)")
                            rescued = True
                            break
                    except Exception as e:
                        log.warning(f"  [RESCUE] {inst} failed: {e}")
                    await asyncio.sleep(random.uniform(8, 15))
                if not rescued:
                    log.warning(f"  [RESCUE] FAIL {s_dt} unresolved - will retry next run")
        finally:
            await nav_rescue.close()

    log.info(f"--- PARALLEL DRILL COMPLETE: {total_new[0]} total new for @{username} ---")
    return []

# ─────────────────────────────────────────────────────────────
#  Incremental Save (after every page)
# ─────────────────────────────────────────────────────────────
def _incremental_save(username: str, new_posts: list, existing: list):
    """Save user file after each page so nothing is lost on crash."""
    # Normalize IDs to strings for safe comparison (JSON may return int or str)
    existing_ids = {str(p["id"]) for p in existing}
    
    # Strip internal helpers before saving
    clean_new = []
    for p in new_posts:
        p_clean = p.copy()
        p_clean.pop("_timestamp_dt", None)
        clean_new.append(p_clean)

    truly_new = [p for p in clean_new if str(p["id"]) not in existing_ids]
    if not truly_new:
        return
     
    combined = truly_new + existing
    combined.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Preserve visual_intel from existing posts - merge into combined by ID
    existing_vi = {p["id"]: p.get("visual_intel") for p in existing if p.get("visual_intel")}
    for p in combined:
        if p["id"] in existing_vi and not p.get("visual_intel"):
            p["visual_intel"] = existing_vi[p["id"]]
    
    user_file = DB_DIR / f"x_intel_{username}.json"
    user_file.write_text(json.dumps(combined, indent=2, ensure_ascii=True), encoding="utf-8")
    log.info(f"  [SAVE] {len(combined)} posts for @{username} ({len(truly_new)} new)")


async def scrape_search_block(nav, url, inst, username):
    """Scrapes a single search block with the standardized pagination engine."""
    return await scrape_pagination_loop(
        nav, url, inst, username, 
        parse_fn=parse_tweet
    )


def _deduplicate_file(username: str):
    """Deep cleanup and deduplication of a user's JSON file.
    Preserves visual_intel fields populated by image_analyzer."""
    user_file = DB_DIR / f"x_intel_{username}.json"
    if not user_file.exists():
        return
    
    try:
        posts = json.loads(user_file.read_text(encoding="utf-8"))
        seen = set()
        deduped = []
        for p in posts:
            pid = str(p["id"])  # Normalize to string for safe dedup
            if pid not in seen:
                # Only re-clean spacing if text has NOT been through translation
                # (raw_text absent = legacy post, safe to clean; raw_text present = translation
                #  may differ from raw_text, so preserve text as-is)
                if "raw_text" not in p:
                    p["text"] = clean_text_spacing(p.get("text", ""))
                    p["raw_text"] = p["text"]  # Back-fill raw_text for legacy posts
                
                # GARBAGE PURGE (check raw_text if available, else text)
                check_text = p.get("raw_text") or p.get("text", "")
                if garbage_purge(check_text):
                    continue
                
                # Explicitly carry visual_intel forward
                # (safety: ensure it's never silently dropped)
                if "visual_intel" not in p:
                    p["visual_intel"] = []
                    
                deduped.append(p)
                seen.add(pid)
        
        deduped.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        user_file.write_text(json.dumps(deduped, indent=2, ensure_ascii=True), encoding="utf-8")
        log.info(f"  Deduplicated @{username}: {len(posts)} -> {len(deduped)} posts.")
    except Exception as e:
        log.error(f"  Failed to deduplicate @{username}: {e}")


# ─────────────────────────────────────────────────────────────
#  Image Downloader (V9.1 - disk-check only, new posts only)
# ─────────────────────────────────────────────────────────────
async def download_images(posts: list, username: str):
    """Download images for the given posts if not already on disk.
    ONLY call with newly-fetched posts - never the full user file.
    Disk presence is the authority: if file exists, skip silently.
    """
    try:
        from curl_cffi import requests as curlr
    except ImportError:
        log.warning("curl_cffi not available - skipping image downloads")
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
                to_download.append((url, local_path, local_name, p))

            # Keep path recorded in post metadata
            if rel_path not in p.get("images", []):
                p.setdefault("images", []).append(rel_path)

    if not to_download:
        return  # Already downloaded - silent

    log.info(f"  IMAGE: {len(to_download)} new images for @{username}")
    saved = 0
    failed_posts = set()
    for url, path, name, post_obj in to_download:
        try:
            # V26.1: Increased stealth delay (2.5s - 5.5s) to avoid instance banning
            await asyncio.sleep(random.uniform(2.5, 5.5))
            
            resp = curlr.get(url, impersonate="chrome110", timeout=15)
            if resp.status_code == 200 and len(resp.content) > 500:
                path.write_bytes(resp.content)
                saved += 1
            elif resp.status_code == 429:
                log.error(f"  IMAGE {name} RATE LIMIT (429). Sleeping 30s...")
                await asyncio.sleep(30)
                failed_posts.add(post_obj["id"])
            else:
                log.warning(f"  IMAGE {name} broken/empty ({resp.status_code}). Queuing VX rescue.")
                failed_posts.add(post_obj["id"])
        except Exception as e:
            log.warning(f"  Image fail ({name}): {e}")
            failed_posts.add(post_obj["id"])

    # If any images failed, secondary VX rescue pass to get fresh URLs
    if failed_posts:
        log.info(f"  RESCUE: Attempting VX rescue for {len(failed_posts)} posts with broken media...")
        # Note: rescue_tweet now has internal 2.5-5.5s delays + 429 backoff
        for p in posts:
            if p["id"] in failed_posts:
                rescue_tweet(p) 

    if saved:
        log.info(f"  IMAGE: Saved {saved}/{len(to_download)} images for @{username}")


def rebuild_master():
    """Rebuild master database from all per-user files.
    DURABILITY: Preserves visual_mentions/visual_last_updated from existing master.
    """
    # Preserve OCR data before overwriting
    master_path = DB_DIR / "x_intel_master.json"
    existing_visual_mentions = {}
    existing_visual_ts = None
    if master_path.exists():
        try:
            old = json.loads(master_path.read_text(encoding="utf-8"))
            existing_visual_mentions = old.get("visual_mentions", {})
            existing_visual_ts = old.get("visual_last_updated")
        except Exception:
            pass

    all_posts = []
    for f in DB_DIR.glob("x_intel_*.json"):
        if f.name == "x_intel_master.json":
            continue
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
            posts = raw if isinstance(raw, list) else raw.get("posts", [])
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
        "posts":               all_posts,
        "buzz":                buzz,
        "last_updated":        now.isoformat(),
        "visual_mentions":     existing_visual_mentions,
        "visual_last_updated": existing_visual_ts,
    }

    # Save master JSON
    master_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    # Save intel.js for dashboard (images stripped - prevents 404 storm)
    def _strip_assets(p):
        c = p.copy(); c.pop("images", None); c.pop("visual_intel", None); return c
    bridge_payload = {**payload, "posts": [_strip_assets(p) for p in all_posts]}
    js_content = ("// GIGACPO Intelligence Data - images stripped for performance\n"
                  "window.X_INTEL_MODULE = " + json.dumps(bridge_payload, ensure_ascii=True) + ";")
    (DB_DIR / "intel.js").write_text(js_content, encoding="utf-8")
    (ROOT / "intel.js").write_text(js_content, encoding="utf-8")

    log.info(f"Master rebuilt: {len(all_posts)} posts, {len(buzz)} tickers, "
             f"{len(existing_visual_mentions)} visual tickers preserved. JS Bridge stripped.")
    return payload




# ─────────────────────────────────────────────────────────────
#  Main - SINGLE USER ONLY
# ─────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(
        description="X Intelligence Scraper V9.1 - Single User | Smart Cache | Parallel Mirrors"
    )
    parser.add_argument(
        "--username", type=str,
        help="Single X handle to scrape. Example: --username aleabitoreddit"
    )
    parser.add_argument("--all", action="store_true", help="Scrape ALL monitored users")
    parser.add_argument("--days", type=int, default=210)
    parser.add_argument("--since", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--query", type=str, default="", help="Additional search keyword")
    parser.add_argument("--instance", type=str, default=None,
                        help="Force a specific mirror instance (optional)")
    args = parser.parse_args()

    # Load shared user list
    USER_FILE = DB_DIR / "monitored_users.json"
    if args.all:
        if not USER_FILE.exists():
            log.error("monitored_users.json not found. Use --username instead.")
            return
        target_users = json.loads(USER_FILE.read_text(encoding="utf-8"))
    elif args.username:
        target_users = [args.username.strip().lstrip("@")]
    else:
        log.error("Must provide --username or --all")
        return

    for user in target_users:
        log.info(f"{'='*60}")
        log.info(f"X INTEL V9.2 | @{user} | Deep Scraper | Custom Filters")
        log.info(f"{'='*60}")

        await scrape_user(
            user, 
            max_days=args.days, 
            instance=args.instance,
            since=args.since,
            until=args.until,
            search_query=args.query
        )

        # Final dedup pass
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

    log.info(f"DONE - @{user} complete. All cleanup scripts executed.")


if __name__ == "__main__":
    asyncio.run(main())