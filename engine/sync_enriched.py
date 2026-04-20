import json
import os
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def sync_enriched():
    master_path = "database/CPO_MASTER_DATA.json"
    bridge_path = "database/dashboard_data.js"
    
    if not os.path.exists(master_path):
        print(f"Error: {master_path} missing.")
        return
        
    with open(master_path, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
            
    # Write JS bridge
    js_content = f"window.CPO_MASTER_DATA = {json.dumps(master_data, indent=2)};"
    with open(bridge_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Total entries: {len(master_data)}")
    print(f"Bridge Synced: {bridge_path}")

if __name__ == "__main__":
    sync_enriched()