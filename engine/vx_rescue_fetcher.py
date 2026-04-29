try:
    from curl_cffi import requests as curlr
except ImportError:
    import requests as curlr

import json
import logging
import random
import re
import sys
import time
from pathlib import Path

# Add project root for StealthNavigator
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "engine"))
try:
    from stealth_navigator import StealthNavigator
except ImportError:
    StealthNavigator = None

# Logging configured by caller
log = logging.getLogger("x_intel.vx_rescue")

# V26.6: Sovereign Multi-Tier Gateway Pool
GATEWAYS = [
    {"url": "https://api.fxtwitter.com/status/{id}", "type": "api"},
    {"url": "https://api.vxtwitter.com/Twitter/status/{id}", "type": "api"},
    {
        "url": "https://fxtwitter.com/status/{id}",
        "type": "og_scrape",
    },  # HTML Fallback 1
    {
        "url": "https://vxtwitter.com/status/{id}",
        "type": "og_scrape",
    },  # HTML Fallback 2
    {"url": "https://fixupx.com/status/{id}", "type": "og_scrape"},  # HTML Fallback 3
]

# Global state for rate-limit management
_LAST_CALL = 0
_SESSION = None
_CALL_COUNT = 0
_GATEWAY_HEALTH = {gw["url"]: {"failures": 0, "backoff_until": 0} for gw in GATEWAYS}
_ADAPTIVE_DELAY = 3.5


def get_session():
    """Rotates session and impersonation profile to avoid fingerprinting."""
    global _SESSION, _CALL_COUNT
    if _SESSION is None or _CALL_COUNT > 12:
        log.info("[STEALTH] Initializing primary Chrome 146 session profile")
        _SESSION = curlr.Session(impersonate="chrome146")
        ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.7000.{random.randint(100,200)} Safari/537.36"
        _SESSION.headers.update(
            {
                "User-Agent": ua,
                "sec-ch-ua": '"Google Chrome";v="146", "Chromium";v="146", "Not=A?Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
            }
        )
        _CALL_COUNT = 0
    _CALL_COUNT += 1
    return _SESSION


def parse_og_tags(html):
    """Extracts high-fidelity media from OpenGraph/Twitter meta tags."""
    images = re.findall(r'property="og:image" content="(.*?)"', html)
    if not images:
        images = re.findall(r'name="twitter:image" content="(.*?)"', html)

    # Try to find text
    text_match = re.search(r'property="og:description" content="(.*?)"', html)
    text = text_match.group(1) if text_match else ""

    # Try to find author
    author_match = re.search(r'property="og:title" content="(.*?)"', html)
    author = author_match.group(1) if author_match else "Twitter"
    if " on X: " in author:
        author = author.split(" on X: ")[0]

    return {"text": text, "user_screen_name": author, "media_urls": list(set(images))}


async def fetch_vx_stealth_fallback(url):
    """Playwright fallback: Grabs the JSON via full browser emulation."""
    if not StealthNavigator:
        return None
    log.info(f"[PLAYWRIGHT] Rescuing via full browser: {url}")
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    try:
        page = await nav.context.new_page()
        await page.goto(url, wait_until="networkidle")
        content = await page.inner_text("body")
        try:
            return json.loads(content)
        except:
            # Try OG scrape on the page content if JSON fails
            html = await page.content()
            return parse_og_tags(html)
    finally:
        await nav.close()


def fetch_vx_tweet(tweet_id):
    """Fetch high-fidelity tweet data using multi-tier gateway pool."""
    global _LAST_CALL, _GATEWAY_HEALTH, _ADAPTIVE_DELAY

    # 1. Mandatory Jitter
    elapsed = time.time() - _LAST_CALL
    wait_time = max(0, _ADAPTIVE_DELAY + random.uniform(0.5, 2.5) - elapsed)
    if wait_time > 0:
        time.sleep(wait_time)

    # 2. Filter Healthy Gateways
    now = time.time()
    available = [gw for gw in GATEWAYS if _GATEWAY_HEALTH[gw["url"]]["backoff_until"] < now]
    if not available:
        time.sleep(30)
        available = GATEWAYS.copy()

    random.shuffle(available)

    for gw in available:
        url = gw["url"].format(id=tweet_id)
        session = get_session()

        try:
            resp = session.get(url, timeout=15)
            _LAST_CALL = time.time()

            if resp.status_code == 200:
                _GATEWAY_HEALTH[gw["url"]]["failures"] = 0
                if gw["type"] == "api":
                    return resp.json()
                else:
                    return parse_og_tags(resp.text)
            elif resp.status_code == 429:
                log.error(f"RATE LIMIT (429) on {url.split('/')[2]}. Demoting.")
                _GATEWAY_HEALTH[gw["url"]]["backoff_until"] = now + 600
                _ADAPTIVE_DELAY = min(12.0, _ADAPTIVE_DELAY + 1.0)
                continue
            else:
                _GATEWAY_HEALTH[gw["url"]]["backoff_until"] = now + 60
                continue
        except Exception:
            continue

    return None


def rescue_tweet(tweet_obj):
    """Attempt to rescue a tweet object with missing or truncated data."""
    tweet_id = tweet_obj.get("id")
    if not tweet_id:
        return tweet_obj

    vx_data = fetch_vx_tweet(tweet_id)
    if not vx_data:
        return tweet_obj

    # Normalized Parser
    tweet_info = vx_data.get("tweet", {}) or vx_data

    # Text
    full_text = tweet_info.get("text", "") or vx_data.get("text", "")
    if full_text and len(full_text) > len(tweet_obj.get("text", "")):
        tweet_obj["text"] = full_text
        tweet_obj["raw_text"] = full_text

    # Author
    author = tweet_info.get("user_screen_name") or tweet_info.get("author", {}).get("screen_name")
    if not author or author == "Twitter":
        author = tweet_obj.get("username", "Unknown")
    log.info(f"Rescued {tweet_id} from @{author}")

    # Media
    media = (
        tweet_info.get("media_urls", [])
        or tweet_info.get("media", {}).get("photos", [])
        or vx_data.get("media_urls", [])
    )
    if media and not tweet_obj.get("image_urls"):
        if isinstance(media, str):
            media = [media]
        tweet_obj["image_urls"] = media
        tweet_obj["images"] = []

    tweet_obj["vx_rescued"] = True
    tweet_obj["vx_fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    return tweet_obj

    tweet_obj["vx_rescued"] = True
    tweet_obj["vx_fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    return tweet_obj


if __name__ == "__main__":
    if len(sys.argv) > 1:
        tid = sys.argv[1]
        print(json.dumps(fetch_vx_tweet(tid), indent=2))
