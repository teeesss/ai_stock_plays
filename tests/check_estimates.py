import asyncio
import json
import os
import sys
import pandas as pd
from datetime import datetime
from curl_cffi import requests
from stealth_navigator import StealthNavigator

# Ensure UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def fetch_enriched_data(tickers=["NVDA", "CRDO"]):
    print(f"🚀 Testing FY26/FY27 Estimates for: {tickers}")
    
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    cookies_list, crumb = await nav.get_session_state(f"https://finance.yahoo.com/quote/{tickers[0]}")
    cookie_dict = {c['name']: c['value'] for c in cookies_list}
    
    session = requests.Session(impersonate="chrome")
    session.headers.update({"User-Agent": nav.current_ua, "Accept": "*/*"})
    session.cookies.update(cookie_dict)
    
    results = {}

    for ticker in tickers:
        print(f"  Processing {ticker}...")
        
        # Modules: earningsTrend gives FY1 and FY2 estimates
        # Modules: defaultKeyStatistics gives forwardPE
        modules = "earningsTrend,defaultKeyStatistics,financialData"
        url_summary = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules={modules}&crumb={crumb}"
        
        try:
            r = session.get(url_summary)
            data = r.json()
            
            summary = data['quoteSummary']['result'][0]
            
            estimates = {}
            trends = summary.get('earningsTrend', {}).get('trend', [])
            
            # FY1 = usually current year (2026), FY2 = next year (2027)
            # We look for periods like "+1y", "0y"
            for t in trends:
                period = t.get('period')
                if period == '0y': # Current Year
                    estimates['FY26_eps'] = t.get('earningsEstimate', {}).get('avg', {}).get('raw')
                if period == '+1y': # Next Year
                    estimates['FY27_eps'] = t.get('earningsEstimate', {}).get('avg', {}).get('raw')
            
            # Forward PE is usually next FY
            estimates['forward_pe'] = summary.get('defaultKeyStatistics', {}).get('forwardPE', {}).get('raw')
            
            # Calculate P/Es if we have EPS
            curr_price = summary.get('financialData', {}).get('currentPrice', {}).get('raw')
            if curr_price:
                if estimates.get('FY26_eps'):
                    estimates['pe_26'] = round(curr_price / estimates['FY26_eps'], 2)
                if estimates.get('FY27_eps'):
                    estimates['pe_27'] = round(curr_price / estimates['FY27_eps'], 2)

            results[ticker] = estimates
            
        except Exception as e:
            print(f"  [!] Failed {ticker}: {e}")

    await nav.close()
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(fetch_enriched_data())
