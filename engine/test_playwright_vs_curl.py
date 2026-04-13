"""Test: Does Playwright actually get tweet content where curl_cffi cannot?"""
import asyncio, json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from stealth_navigator import StealthNavigator
from bs4 import BeautifulSoup

async def test():
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    
    # Test the instance that was working in the user's browser
    test_urls = [
        "https://nitter.tiekoetter.com/KawzInvests",
        "https://xcancel.com/KawzInvests",
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"TESTING: {url}")
        print(f"{'='*60}")
        
        page = await nav.context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(8)  # Wait for JS rendering
            
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            tweets = soup.select(".tweet-content")
            dates = soup.select(".tweet-date a")
            showmore = soup.select(".show-more a")
            
            print(f"  Tweets found:  {len(tweets)}")
            print(f"  Dates found:   {len(dates)}")
            print(f"  Has pagination: {len(showmore) > 0}")
            
            if showmore:
                print(f"  Cursor href:   {showmore[0].get('href', '')[:80]}")
            
            if tweets:
                for i, t in enumerate(tweets[:3]):
                    print(f"  Tweet {i+1}: {t.get_text(strip=True)[:100]}...")
                    
            if dates:
                for i, d in enumerate(dates[:3]):
                    print(f"  Date {i+1}: {d.get('title','')}")
            
            # Also check images
            imgs = soup.select(".attachment.image img")
            print(f"  Images found:  {len(imgs)}")
            if imgs:
                for img in imgs[:2]:
                    src = img.get("data-src") or img.get("src", "")
                    print(f"    img src: {src[:80]}")
                    
        except Exception as e:
            print(f"  ERROR: {e}")
        finally:
            await page.close()
    
    await nav.close()

asyncio.run(test())
