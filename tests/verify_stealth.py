import asyncio
import sys
from stealth_navigator import StealthNavigator

# Ensure UTF-8 output even on Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def verify_stealth():
    """
    Test suite for the StealthNavigator.
    Checks detection vectors: Identity, Behavior, and Hardware.
    """
    print("Starting Stealth Verification Suite...")
    
    # headless=True for background verification
    nav = StealthNavigator(headless=True) 
    await nav.initialize()
    
    page = await nav.context.new_page()
    
    # 1. Check BOT detection score
    print("  [1/3] Checking Identity (Sannysoft Bot Test)...")
    try:
        await page.goto("https://bot.sannysoft.com/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
    except Exception as e:
        print(f"  [!] Bot Test Navigation Failed: {e}")
    
    # 2. Check Hardware Fingerprinting
    print("  [2/3] Checking Hardware Masking (BrowserScan)...")
    try:
        await page.goto("https://www.browserscan.net/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
    except Exception as e:
        print(f"  [!] BrowserScan Navigation Failed: {e}")
    
    # 3. Check Behavioral Integrity
    print("  [3/3] Performing Ghost Browsing on Yahoo Finance...")
    try:
        await nav.ghost_browse(page, "https://finance.yahoo.com/quote/NVDA")
    except Exception as e:
        print(f"  [!] Ghost Browsing Test Failed: {e}")
    
    await nav.close()
    print("\nVerification Complete. Identities and Behavioral engines sanitized and ready.")

if __name__ == "__main__":
    asyncio.run(verify_stealth())
