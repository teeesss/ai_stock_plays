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

async def fetch_enriched_data(base_tickers=["NVDA", "CRDO", "BESIY", "KLIC", "ENTG", "ONTO", "DNPCY"]):
    print(f"🚀 Phase III: Estimating + Weekly History for {len(base_tickers)} stocks")
    
    nav = StealthNavigator(headless=True)
    await nav.initialize()
    cookies_list, crumb = await nav.get_session_state(f"https://finance.yahoo.com/quote/{base_tickers[0]}")
    cookie_dict = {c['name']: c['value'] for c in cookies_list}
    
    session = requests.Session(impersonate="chrome")
    session.headers.update({"User-Agent": nav.current_ua, "Accept": "*/*"})
    session.cookies.update(cookie_dict)
    
    output_path = "database/enriched_test_data.json"
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            enriched_results = json.load(f)
    else:
        enriched_results = {}

    for ticker in base_tickers:
        print(f"  Processing {ticker}...")
        
        # 1. Weekly History (5y)
        url_chart = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5y&interval=1wk"
        
        # 2. Estimates & CAGR
        modules = "earningsTrend,defaultKeyStatistics,financialData,incomeStatementHistory"
        url_summary = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules={modules}&crumb={crumb}"
        
        try:
            r_chart = session.get(url_chart)
            r_summary = session.get(url_summary)
            
            chart_data = r_chart.json() if r_chart.status_code == 200 else {}
            summary_data = r_summary.json() if r_summary.status_code == 200 else {}
            
            # --- Weekly History for ApexCharts ---
            history = []
            if 'chart' in chart_data and chart_data['chart']['result']:
                res = chart_data['chart']['result'][0]
                timestamps = res['timestamp']
                closes = res['indicators']['adjclose'][0]['adjclose']
                # Pair timestamps with closes for accurate charting
                for ts, cl in zip(timestamps, closes):
                    if cl is not None:
                        history.append({"x": ts * 1000, "y": round(cl, 2)})

            # --- Forward P/E Estimates ---
            estimates = {}
            if 'quoteSummary' in summary_data and summary_data['quoteSummary']['result']:
                sum_res = summary_data['quoteSummary']['result'][0]
                trends = sum_res.get('earningsTrend', {}).get('trend', [])
                curr_price = sum_res.get('financialData', {}).get('currentPrice', {}).get('raw')
                
                for t in trends:
                    period = t.get('period')
                    eps_avg = t.get('earningsEstimate', {}).get('avg', {}).get('raw')
                    if period == '0y' and eps_avg and curr_price:
                        estimates['pe_26'] = round(curr_price / eps_avg, 2)
                    if period == '+1y' and eps_avg and curr_price:
                        estimates['pe_27'] = round(curr_price / eps_avg, 2)
                
                # Revenue History for CAGR
                revenue_history = []
                income = sum_res.get('incomeStatementHistory', {}).get('incomeStatementHistory', [])
                for yr in income:
                    if 'totalRevenue' in yr:
                        revenue_history.append({"date": yr['endDate'].get('fmt'), "val": yr['totalRevenue'].get('raw')})
                
                rev_growth = {}
                if len(revenue_history) >= 2:
                    curr_rev = revenue_history[0]['val']
                    oldest_rev = revenue_history[-1]['val']
                    n_years = len(revenue_history) - 1
                    if oldest_rev and curr_rev and n_years > 0:
                        rev_growth['cagr'] = round(((curr_rev / oldest_rev) ** (1/n_years) - 1) * 100, 2)

            # Update results
            enriched_results[ticker] = {
                "history": history,
                "estimates": estimates,
                "performance": enriched_results.get(ticker, {}).get('performance', {}), # Keep existing
                "revenue_trends": {
                    "growth": rev_growth if 'rev_growth' in locals() else {}
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  [!] Failed {ticker}: {e}")

    await nav.close()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_results, f, indent=2)
    print(f"✅ Enriched data (Weekly + Estimates) saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(fetch_enriched_data())
