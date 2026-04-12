import csv
import json
import os
from datetime import datetime

CSV_PATH = 'cpo_master_ultimate.csv'
SNAPSHOT_PATH = 'research/audit_snapshot_20260411_220428.json'
MASTER_JSON_PATH = 'research/CPO_MASTER_DATA.json'

def initialize_master():
    master_data = {}
    
    # 1. Load CSV (Human Research)
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row['Ticker'].strip()
                if not ticker: continue
                master_data[ticker] = {
                    "human_research": row,
                    "financials": {},
                    "last_updated": datetime.now().isoformat()
                }
    
    # 2. Load Snapshot (Automated Financials)
    if os.path.exists(SNAPSHOT_PATH):
        with open(SNAPSHOT_PATH, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
            for ticker, data in snapshot.items():
                if ticker in master_data:
                    master_data[ticker]["financials"] = data
                    master_data[ticker]["last_updated"] = datetime.now().isoformat()
                else:
                    # New ticker found in snapshot but not in CSV (unlikely but handle)
                    master_data[ticker] = {
                        "human_research": {},
                        "financials": data,
                        "last_updated": datetime.now().isoformat()
                    }

    # 3. Save Master
    os.makedirs("research", exist_ok=True)
    with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=2)
    
    print(f"Master JSON Initialized with {len(master_data)} entries.")
    print(f"Path: {MASTER_JSON_PATH}")

if __name__ == "__main__":
    initialize_master()
