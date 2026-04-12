import csv
import os

def clean_and_extend_csv(csv_path):
    # Data Mapping for 300% Moonshots (3x, 5x, 10x Potential)
    upside_map = {
        "POET": "10x",
        "LWLG": "10x",
        "AAOI": "5x",
        "AXTI": "5x",
        "ALAB": "3x", 
        "PLET.DE": "5x",
        "SMHN.DE": "3x",
        "BESIY": "3x",
        "CRDO": "3x",
        "LITE": "3x",
        "COHR": "3x",
        "ALRIB.PA": "5x",
        "2455.TW": "5x",
        "SMTOY": "3x",
        "AYAR": "10x",
        "SCINTIL": "10x",
        "RANV": "10x"
    }

    if not os.path.exists(csv_path):
        return

    # Read and clean
    updated_rows = []
    with open(csv_path, mode='r', encoding='utf-8') as f:
        # We manually parse to fix potential formatting drift
        lines = f.readlines()
        header = lines[0].strip().split(',')
        if "Target Upside" not in header:
            header.append("Target Upside")
        
        for line in lines[1:]:
            parts = line.strip().split(',')
            # Ensure we have enough columns (filling empty if needed)
            while len(parts) < len(header) - 1:
                parts.append("TBD")
            
            ticker = parts[0].strip()
            # Assign Upside
            upside = upside_map.get(ticker, "1x-2x")
            
            # Ensure we don't exceed header count
            if len(parts) < len(header):
                parts.append(upside)
            else:
                parts[len(header)-1] = upside
                
            updated_rows.append(parts)

    # Write back
    with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)
    
    print(f"CSV Schema updated and cleaned. Target Upside column added.")

if __name__ == "__main__":
    clean_and_extend_csv('cpo_master_ultimate.csv')
    os.system('python research/sync_data.py')
