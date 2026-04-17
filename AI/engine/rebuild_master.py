import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../engine')))

import json, os, datetime

MASTER_FILE = r"z:\COS_Stock_Plays\AI\database\AI_MASTER_DATA.json"
JS_OUT = r"z:\COS_Stock_Plays\AI\database\dashboard_data.js"

def rebuild():
    with open(MASTER_FILE, "r") as f:
        master = json.load(f)

    # Output pure JSON object for client, mimicking CPO_MASTER_DATA
    payload = {}
    
    for symbol, dt in master.items():
        if dt.get("no_dashboard"):
            continue
            
        obb = dt.get("openbb_supplement", {})
        
        # Build the wrapper object expected by index.html exactly
        payload[symbol] = {
            "human_research": {
                "Role": dt.get("Role / Notes", ""),
                "Notes": dt.get("Role / Notes", ""),
                "Country": dt.get("Country", "US"),
                "Bucket": dt.get("Bucket", "AI Watchlist"),
                "Alpha Score": dt.get("Alpha_Score", 0)
            },
            "openbb_supplement": obb,
            "financials": dt.get("financials", {})
        }
        
    js = f"window.CPO_MASTER_DATA = {json.dumps(payload)};"
    with open(JS_OUT, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"Rebuilt dashboard_data.js ({len(payload)} entries)")

if __name__ == '__main__':
    rebuild()
