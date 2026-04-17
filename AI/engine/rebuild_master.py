import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../engine')))

import json, os, datetime

MASTER_FILE = r"z:\COS_Stock_Plays\AI\database\AI_MASTER_DATA.json"
JS_OUT = r"z:\COS_Stock_Plays\AI\database\dashboard_data.js"

def rebuild():
    with open(MASTER_FILE, "r") as f:
        master = json.load(f)

    # Output pure JSON string for client
    base_obj = {"last_updated": datetime.datetime.now().isoformat()}
    payload = []
    
    for symbol, dt in master.items():
        if dt.get("no_dashboard"):
            continue
            
        obb = dt.get("openbb_supplement", {})
        
        entry = {
            "ticker": symbol,
            "category": dt.get("Bucket", "Unknown"),
            "role": dt.get("Role / Notes", ""),
            "country": dt.get("Country", "US"),
            "pe26": dt.get("PE_2026", 0),
            "pe27": dt.get("PE_2027", 0),
            "rev_cagr": dt.get("Rev_CAGR", 0),
            "score": dt.get("Alpha_Score", 0),
            "buzz": {"1d":0, "3d":0, "7d":0}, # Empty buzz for now
            "obb": obb
        }
        payload.append(entry)
        
    js = f"window.DASHBOARD_DATA = {json.dumps(payload)};"
    with open(JS_OUT, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"Rebuilt dashboard_data.js ({len(payload)} entries)")

if __name__ == '__main__':
    rebuild()
