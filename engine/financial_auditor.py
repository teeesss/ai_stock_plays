import csv
import os
import asyncio
import time
import random
import re
import sys
import json
from datetime import datetime
from curl_cffi import requests
from yahoo_auth import get_valid_auth

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MASTER_JSON_PATH = 'database/CPO_MASTER_DATA.json'

async def audit_financials(csv_path, max_tickers=None):
    """
    Ultimate Stealth Auditor (V4.1) - Authoritative JSON Mode
    Hybrid Engine + Full Financial IQ + Persistent Master Storage.
    """
    if not os.path.exists(MASTER_JSON_PATH):
        print(f"Error: {MASTER_JSON_PATH} not found. Run initialize_master.py first.")
        return

    # Load Authoritative JSON
        # Load Authoritative JSON
    with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    # 1. RANDOMIZED HEATING (Layer 1 Stealth)
    valid_tickers = [t for t, e in master_data.items() if e.get("human_research", {}).get("Status") != "Private"]

    print(f"[RUN] Starting Deep Brain Audit (V4.4) on {len(master_data)} authoritative entries...")
    
    # Session State
    nav = None
    client = None
    crumb = ""
    failures = []
    processed_count = 0
    updated_count = 0
    
    async def heat_session():
        nonlocal client, crumb
        print("? Retrieving decoupled stealth session...")
        try:
            cookie_dict, crumb, user_agent = await get_valid_auth()
            client = requests.Session(impersonate="chrome146")
            client.headers.update({"User-Agent": user_agent, "Accept": "*/*"})
            client.cookies.update(cookie_dict)
            print(f"  Session Active. | Crumb: {crumb[:8]}...")
        except Exception as e:
            print(f"  [!] Session failed: {e}")
            client = None

    def clean_ticker(ticker):
        """Extract primary ticker from compound format 'A.XX / B' -> 'A.XX'."""
        return ticker.split(' / ')[0].strip()

    def get_ticker_variants(ticker):
        variants = [ticker]
        m_map = {
            "ASMPT": ["0522.HK", "ASMPF"], "INRI": ["0166.KL"], "EOPT": ["300502.SZ"],
            "IBIEY": ["4062.T"], "TWCPY": ["6315.T"], "AIXNY": ["AIXA.DE"],
            "SHWDY": ["4004.T"], "DNPCY": ["7912.T"], "MYCRF": ["MYCR.ST"],
        }
        if ticker in m_map: variants.extend(m_map[ticker])
        if ":" in ticker:
            parts = ticker.split(":"); variants.append(f"{parts[1]}.T") if "TYO" in parts[0] else None
            variants.append(f"{parts[1]}.DE") if "FRA" in parts[0] else None
        if ticker.endswith(".TW"): variants.append(ticker.replace(".TW", ".TWO"))
        if ticker.endswith(".TWO"): variants.append(ticker.replace(".TWO", ".TW"))
        clean_variants = [v.split(":")[-1] if ":" in v else v for v in variants]
        return list(dict.fromkeys(clean_variants))

    await heat_session()

    try:
        for ticker, entry in master_data.items():
            if max_tickers and processed_count >= max_tickers: break
            
            status = entry.get("human_research", {}).get("Status", "Public")
            if status == "Private": continue

            if processed_count > 0 and processed_count % 30 == 0:
                await heat_session()

            primary_ticker = clean_ticker(ticker)
            variants = get_ticker_variants(primary_ticker)
            data_found = False
            
            for v_ticker in variants:
                print(f"  [{ticker}] Trying {v_ticker}... ({processed_count + 1}/{len(master_data)})", end="\r")
                sys.stdout.flush()
                
                if not client: continue
                try:
                    modules = "price,summaryDetail,defaultKeyStatistics,financialData,earningsTrend"
                    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{v_ticker}?modules={modules}&crumb={crumb}"
                    resp = client.get(url, timeout=12)
                    
                    if resp.status_code == 200:
                        result = resp.json().get('quoteSummary', {}).get('result', [{}])[0]
                        if result:
                            entry["financials"] = result
                            entry["last_updated"] = datetime.now().isoformat()
                            updated_count += 1
                            data_found = True
                            break 
                except Exception as e:
                    pass
            
            processed_count += 1
            if processed_count % 10 == 0:
                with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
                    json.dump(master_data, f, indent=2)
    finally:
        # FINAL JSON EXPORT
        with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2)
    
    print(f"\n[OK] Audit Complete. Updated {updated_count} authoritative entries in {MASTER_JSON_PATH}")

    # TRIGGER SYNC to CSV and HTML
    try:
        from generate_CPO_BRAIN import generate_brain_from_master
        generate_brain_from_master(MASTER_JSON_PATH)
    except Exception as e:
        print(f"Warning: Sync failed: {e}")

if __name__ == "__main__":
    # Robust loop handling for Windows
    async def main():
        await audit_financials('cpo_master_ultimate.csv')
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Critical Error: {e}")