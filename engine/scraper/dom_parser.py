import re
import sys
import logging
from datetime import datetime, timezone
from bs4 import BeautifulSoup

log = logging.getLogger("x_intel.dom")

def parse_date(raw: str) -> datetime:
    """Parses nitter date strings."""
    now = datetime.now(timezone.utc)
    try:
        # 'Apr 13, 2026 · 12:36 AM UTC'
        clean = raw.split('·')[0].strip()
        dt = datetime.strptime(clean, "%b %d, %Y")
        return dt.replace(tzinfo=timezone.utc)
    except:
        # Handle '5h', '20m', etc.
        m = re.match(r'(\d+)([hmd])', raw)
        if m:
            val, unit = int(m.group(1)), m.group(2)
            if unit == 'h': return now - timedelta(hours=val)
            if unit == 'm': return now - timedelta(minutes=val)
            if unit == 'd': return now - timedelta(days=val)
        return now

def clean_text_spacing(text: str) -> str:
    """Removes double-spacing and cleans up character fragments."""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def garbage_purge(text: str) -> bool:
    """Returns True if the text is pure garbage/noise."""
    if not text: return True
    if len(text) < 10: return True
    # Crypto spam indicators
    if 'Airdrop' in text and 'Solana' in text: return True
    return False

def parse_tweet(item, username: str) -> dict:
    """Parses a single nitter timeline item into a standard dict."""
    cd = item.select_one(".tweet-content")
    dl = item.select_one(".tweet-date a")
    if not cd or not dl:
        return None
    
    if item.select_one(".pinned"):
        return None
        
    tweet_id = dl.get("href", "").split("/")[-1].split("#")[0]
    raw_date = dl.get("title", "")
    
    # We use local parse_date if available or just return raw for now
    # Scraper will handle precise DT conversion
    
    content_copy = BeautifulSoup(str(cd), "html.parser")
    for cashtag_el in content_copy.select("a.cashtag, a[href*='/search?q=%24']"):
        ticker_text = cashtag_el.get_text(separator="", strip=True)
        cashtag_el.replace_with(f" {ticker_text} ")
    
    raw_text = content_copy.get_text(separator=" ", strip=True)
    text = re.sub(r'\s+', ' ', raw_text).strip()
    
    if garbage_purge(text):
        return None

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
        "raw_text": text,
        "raw_date": raw_date,
        "images": local_paths,
        "image_urls": img_urls,
        "url": f"https://x.com/{username}/status/{tweet_id}",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
