"""Probe Nitter instances to find which ones actually return tweet data."""
from curl_cffi import requests as r
from bs4 import BeautifulSoup
import time, json

instances = [
    "https://xcancel.com",
    "https://nitter.tiekoetter.com",
    "https://nitter.poast.org",
    "https://nitter.cz",
    "https://nitter.it",
    "https://nitter.private.coffee",
    "https://nitter.rawbit.ninja",
    "https://nitter.projectsegfau.lt",
    "https://nitter.perennialte.ch",
]

username = "KawzInvests"
results = []

for inst in instances:
    url = f"{inst}/{username}"
    try:
        resp = r.get(url, impersonate="chrome110", timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".timeline-item")
        tweets = soup.select(".tweet-content")
        showmore = soup.select(".show-more a")
        dates = soup.select(".tweet-date a")
        
        status = {
            "instance": inst,
            "http": resp.status_code,
            "tweets_found": len(tweets),
            "dates_found": len(dates),
            "has_pagination": len(showmore) > 0,
            "response_bytes": len(resp.text),
        }
        
        if tweets:
            status["first_tweet_preview"] = tweets[0].get_text(strip=True)[:100]
        if dates:
            status["first_date"] = dates[0].get("title", "")
        if showmore:
            status["cursor_href"] = showmore[0].get("href", "")
        
        results.append(status)
        verdict = "LIVE" if len(tweets) > 0 else "DEAD"
        print(f"[{verdict}] {inst:45s} => HTTP {resp.status_code}, {len(tweets)} tweets, pagination={len(showmore)>0}")
        
    except Exception as e:
        results.append({"instance": inst, "error": str(e)[:80]})
        print(f"[FAIL] {inst:45s} => {str(e)[:80]}")
    
    time.sleep(2)

# Save results
with open("database/instance_probe.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved. {sum(1 for r in results if r.get('tweets_found',0)>0)} live instances found.")