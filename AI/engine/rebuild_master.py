import sys, os, json, datetime
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../engine')))

ROOT = Path(__file__).parent.parent
MASTER_FILE = ROOT / "database" / "AI_MASTER_DATA.json"
RESEARCH_FILE = ROOT / "database" / "AI_RESEARCH_DATA.json"
JS_OUT = ROOT / "database" / "dashboard_data.js"

def rebuild():
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        master = json.load(f)
    
    research = {}
    if RESEARCH_FILE.exists():
        with open(RESEARCH_FILE, "r", encoding="utf-8") as f:
            research = json.load(f)

    # Bridge root intelligence (Shared resource)
    intel_master_path = ROOT.parent / "database" / "x_intel_master.json"
    intel_master = {}
    if intel_master_path.exists():
        with open(intel_master_path, "r", encoding="utf-8") as f:
            intel_master = json.load(f)
    
    global_visual = intel_master.get("visual_mentions", {})
    global_buzz = intel_master.get("mentions", {})

    # Output pure JSON object for client, mimicking CPO_MASTER_DATA
    payload = {}
    
    for symbol, dt in master.items():
        if dt.get("no_dashboard"):
            continue
            
        r_info = research.get(symbol, {})
        
        # Supplemental data resolution: Research override > Master human_research > Master financials fallback
        r_supp = r_info.get("openbb_supplement", {})
        m_supp = dt.get("human_research", {}).get("openbb_supplement", {})
        
        # Build the wrapper object expected by index.html exactly
        payload[symbol] = {
            "human_research": {
                "Company": r_info.get("Company Name") or dt.get("Company Name", symbol),
                "Role": r_info.get("Role", ""),
                "Notes": r_info.get("Notes", ""),
                "Country": dt.get("financials", {}).get("price", {}).get("exchange", "US"),
                "Bucket": r_info.get("Bucket") or dt.get("Bucket", "AI Watchlist"),
                "Alpha Score": r_info.get("Alpha Score", 8.2),
                "Risk Adj": r_info.get("Risk Adj", 3),
                "Hiddenness": r_info.get("Hiddenness", 5),
                "Target Upside": r_info.get("Target Upside") or (f"{r_supp.get('analyst_implied_upside_pct') or m_supp.get('analyst_implied_upside_pct')}%" if (r_supp.get('analyst_implied_upside_pct') or m_supp.get('analyst_implied_upside_pct')) else None) or dt.get("Target_Upside") or "+45%"
            },
            "performance": {
                "1y": r_supp.get("perf_1y") or m_supp.get("perf_1y"),
                "recent_7d_status": r_supp.get("recent_7d_status") or m_supp.get("recent_7d_status")
            },
            "buzz": global_buzz.get(symbol, {}),
            "visual_mentions": global_visual.get(symbol, []),
            "openbb_supplement": {
                "analyst_count": r_supp.get("analyst_count") or m_supp.get("analyst_count") or dt.get("financials", {}).get("financialData", {}).get("numberOfAnalystOpinions", {}).get("raw"),
                "inst_ownership_pct": r_supp.get("inst_ownership_pct") or m_supp.get("inst_ownership_pct") or (round(dt.get("financials", {}).get("defaultKeyStatistics", {}).get("heldPercentInstitutions", {}).get("raw", 0) * 100, 1) if dt.get("financials", {}).get("defaultKeyStatistics", {}).get("heldPercentInstitutions", {}).get("raw") else None),
                "short_interest_pct": r_supp.get("short_interest_pct") or m_supp.get("short_interest_pct") or (round(dt.get("financials", {}).get("defaultKeyStatistics", {}).get("sharesPercentSharesOut", {}).get("raw", 0) * 100, 1) if dt.get("financials", {}).get("defaultKeyStatistics", {}).get("sharesPercentSharesOut", {}).get("raw") else None)
            },
            "financials": dt.get("financials", {})
        }
        
    js = f"window.CPO_MASTER_DATA = {json.dumps(payload)};\n"
    # Also include timestamp
    js += f"window.DASHBOARD_METADATA = {{'last_rebuild': '{datetime.datetime.now().isoformat()}'}};"
    
    with open(JS_OUT, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"Rebuilt dashboard_data.js ({len(payload)} entries)")

if __name__ == '__main__':
    rebuild()
