import requests
import json
import logging
import time
import random
from pathlib import Path

# Configure logging
ROOT = Path(__file__).parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "vx_rescue.log"), logging.StreamHandler()]
)
log = logging.getLogger("vx_rescue")

def fetch_vx_tweet(tweet_id):
    """Fetch high-fidelity tweet data from api.vxtwitter.com."""
    url = f"https://api.vxtwitter.com/Twitter/status/{tweet_id}"
    try:
        # Use headers to look like a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            log.warning(f"VX API error {resp.status_code} for {tweet_id}")
            return None
    except Exception as e:
        log.error(f"Failed to fetch VX {tweet_id}: {e}")
        return None

def rescue_tweet(tweet_obj):
    """Attempt to rescue a tweet object with missing or truncated data."""
    tweet_id = tweet_obj.get("id")
    if not tweet_id:
        return tweet_obj
        
    vx_data = fetch_vx_tweet(tweet_id)
    if not vx_data:
        return tweet_obj
        
    # Enrich
    log.info(f"Rescued {tweet_id} from @{vx_data.get('user_screen_name')}")
    
    # Priority update: text
    full_text = vx_data.get("text", "")
    if full_text and len(full_text) > len(tweet_obj.get("text", "")):
        tweet_obj["text"] = full_text
        tweet_obj["raw_text"] = full_text
        
    # Priority update: media
    media = vx_data.get("media_urls", [])
    if media and not tweet_obj.get("image_urls"):
        tweet_obj["image_urls"] = media
        # Reset local paths so they get re-downloaded if missing
        tweet_obj["images"] = [] 
        
    tweet_id_str = str(tweet_id)
    tweet_obj["vx_rescued"] = True
    tweet_obj["vx_fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    return tweet_obj

if __name__ == "__main__":
    # Test with a known ID if provided
    import sys
    if len(sys.argv) > 1:
        tid = sys.argv[1]
        print(json.dumps(fetch_vx_tweet(tid), indent=2))
