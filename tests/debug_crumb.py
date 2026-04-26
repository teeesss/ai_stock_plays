import asyncio
import os
import sys

# Add research to path
sys.path.append(os.path.join(os.getcwd(), "research"))
from stealth_navigator import StealthNavigator


async def test_crumb():
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    cookies, crumb = await nav.get_session_state("https://finance.yahoo.com/quote/NVDA")
    print(f"Crumb Found: '{crumb}'")
    print(f"Cookies Count: {len(cookies)}")
    await nav.close()


if __name__ == "__main__":
    asyncio.run(test_crumb())
