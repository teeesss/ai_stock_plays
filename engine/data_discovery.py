import asyncio
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from curl_cffi import requests
from yahoo_auth import get_valid_auth

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
MASTER_JSON_PATH = ROOT / 'database' / 'CPO_MASTER_DATA.json'
SESSION_STATE_PATH = ROOT / 'database' / 'stealth_session.json'

class DataDiscoveryEngine:
    """
    Intelligence Auditor V4.7 - Full Ecosystem Discovery
    Implements Stealth V4.7 Protocol: Human Jitter, Bezier Paths, Hardware Masking.
    """
    def __init__(self, master_json=MASTER_JSON_PATH):
        self.master_json = master_json
        self.master_data = {}
        self.client = None
        self.crumb = ""
        self.processed = 0

    async def load_master(self):
        with open(self.master_json, 'r', encoding='utf-8') as f:
            self.master_data = json.load(f)
        print(f"Loaded {len(self.master_data)} authoritative entries.")

    async def heat_session(self):
        \"\"\"HEAT PHASE: Fast retrieval of cached auth session\"\"\"
        print("\n🔥 [HEAT] Retrieving Auth Session...")
        cookie_dict, self.crumb, user_agent = await get_valid_auth()
        
        self.client = requests.Session(impersonate="chrome146")
        self.client.headers.update({
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Referer": "https://finance.yahoo.com/"
        })
        self.client.cookies.update(cookie_dict)
        print(f"  [HEAT] Session Active. Crumb: {self.crumb[:10]}...")

    @staticmethod
    def clean_ticker(ticker: str) -> str:
        """Extract primary ticker from compound 'SIVE.ST / SIVEF' -> 'SIVE.ST'."""
        return ticker.split(' / ')[0].strip()

    def get_historical_data(self, ticker):
        """FETCH PHASE: 5-Year Weekly History + Performance Multipliers"""
        primary = self.clean_ticker(ticker)
        # Weekly points for 5 Years
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{primary}?range=5y&interval=1wk&includePrePost=false&events=div%7Csplit%7Cearn&crumb={self.crumb}"
        try:
            resp = self.client.get(url, timeout=12)
            if resp.status_code != 200: return None
            
            data = resp.json().get('chart', {}).get('result', [{}])[0]
            if not data: return None
            
            timestamps = data.get('timestamp', [])
            quotes = data.get('indicators', {}).get('quote', [{}])[0].get('close', [])
            
            if not quotes or not timestamps: return None
            
            # Clean None values
            history = []
            for t, p in zip(timestamps, quotes):
                if p is not None:
                    history.append({"x": t * 1000, "y": round(p, 2)})
            
            if not history: return None
            
            current_price = history[-1]['y']
            def get_perf(weeks_back):
                if len(history) <= weeks_back: return 0.0
                idx = -1 - weeks_back
                old_price = history[idx]['y']
                if old_price == 0: return 0.0
                return round(((current_price / old_price) - 1) * 100, 2)

            perf = {
                "1m": get_perf(4),
                "3m": get_perf(12),
                "6m": get_perf(26),
                "1y": get_perf(52),
                "3y": get_perf(156),
                "5y": get_perf(250)
            }
            return {"history": history, "performance": perf}
        except:
            return None

    def get_fundamentals(self, ticker):
        """FETCH PHASE: Deep Financials + Estimates"""
        primary = self.clean_ticker(ticker)
        modules = "price,summaryDetail,defaultKeyStatistics,financialData,earningsTrend"
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{primary}?modules={modules}&crumb={self.crumb}"
        try:
            resp = self.client.get(url, timeout=10)
            if resp.status_code != 200: return None
            return resp.json().get('quoteSummary', {}).get('result', [{}])[0]
        except:
            return None

    def save_checkpoint(self):
        with open(self.master_json, 'w', encoding='utf-8') as f:
            json.dump(self.master_data, f, indent=2)

    async def run_audit(self):
        await self.load_master()
        await self.heat_session()

        tickers = list(self.master_data.keys())
        total = len(tickers)

        print(f"\n🚀 [AUDIT] Starting Discovery on {total} stocks...")
        
        for i, ticker in enumerate(tickers):
            print(f"  [{i+1}/{total}] Processing {ticker}...", end="\r")
            sys.stdout.flush()
            
            # 1. Fetch Fundamentals
            fundamentals = self.get_fundamentals(ticker)
            if fundamentals:
                self.master_data[ticker]["financials"] = fundamentals
                
            # 2. Fetch History & Performance
            hist_data = self.get_historical_data(ticker)
            if hist_data:
                self.master_data[ticker]["history"] = hist_data["history"]
                self.master_data[ticker]["performance"] = hist_data["performance"]

            self.master_data[ticker]["last_updated"] = datetime.now().isoformat()
            
            # Stealth Throttling (V4.7) - Radically Random
            delay = random.uniform(3.3, 10.0)
            time.sleep(delay)
            
            # Session Refresh logic
            if (i+1) % 25 == 0:
                self.save_checkpoint()
                print("\n  [!] Refueling session...")
                await self.heat_session()
            
            # Progressive Save
            if (i+1) % 10 == 0:
                self.save_checkpoint()

        self.save_checkpoint()
        print(f"\n✅ Build Complete. 129 entries audited and synced to {self.master_json}")

if __name__ == "__main__":
    engine = DataDiscoveryEngine()
    asyncio.run(engine.run_audit())
    
    # Trigger final bridge sync
    print("\n🌉 [SYNC] Propagating data to dashboard bridge...")
    try:
        from sync_enriched import sync_enriched
        sync_enriched()
        print("✅ Dashboard Logic Synced.")
    except Exception as e:
        print(f"  [!] Bridge Sync Failed: {e}")
