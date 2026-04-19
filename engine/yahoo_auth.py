
"""
engine/yahoo_auth.py
====================
Provides caching and validity-checking for Yahoo Finance API authentication.
Decouples the slow, heavy Headless Chrome `StealthNavigator` from the hyper-fast `curl_cffi` fetchers.
"""
import json
import time
import asyncio
from pathlib import Path
from curl_cffi import requests
from stealth_navigator import StealthNavigator, USER_AGENTS

ROOT = Path(__file__).parent.parent
AUTH_FILE = ROOT / 'database' / 'auth_state.json'
TTL_SECONDS = 12 * 3600  # 12 hours

def is_crumb_valid(cookie_dict: dict, crumb: str, user_agent: str) -> bool:
    """Check if the crumb and cookies are still valid for v7 quotes."""
    try:
        url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL&crumb={crumb}'
        client = requests.Session(impersonate='chrome146')
        client.headers.update({"User-Agent": user_agent})
        client.cookies.update(cookie_dict)
        res = client.get(url, timeout=10)
        return res.status_code == 200
    except Exception:
        return False

async def get_valid_auth():
    """
    Returns (cookie_dict, crumb, user_agent).
    Checks cache first, re-validates via a lightweight curl_cffi check,
    and if invalid/expired, kicks off StealthNavigator to rebuild it.
    """
    if AUTH_FILE.exists():
        try:
            with open(AUTH_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Use cached if within TTL
            if time.time() - data.get('timestamp', 0) < TTL_SECONDS:
                cookie_dict = data.get('cookie_dict', {})
                crumb = data.get('crumb', '')
                ua = data.get('user_agent', USER_AGENTS[0])
                
                # Check validity on the wire
                if is_crumb_valid(cookie_dict, crumb, ua):
                    return cookie_dict, crumb, ua
                else:
                    print("[AUTH] Cached crumb invalid or expired. Fetching new one...")
        except Exception as e:
            print(f"[AUTH] Error reading auth cache: {e}")

    print("[AUTH] Spinning up StealthNavigator to harvest new Yahoo authentication...")
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    cookies_list, crumb = await nav.get_session_state('https://finance.yahoo.com/quote/AAPL')
    await nav.close()
    
    cookie_dict = {c['name']: c['value'] for c in cookies_list}
    ua = nav.current_ua
    
    with open(AUTH_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'cookie_dict': cookie_dict,
            'crumb': crumb,
            'user_agent': ua,
            'timestamp': time.time()
        }, f, indent=2)
        
    return cookie_dict, crumb, ua
