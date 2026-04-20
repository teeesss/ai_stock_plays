import csv
import json
import os
import re
from datetime import datetime

# PATHS
MASTER_JSON = "database/CPO_MASTER_DATA.json"
BRAIN_JSON = "database/CPO_BRAIN.json"
BRAIN_MD = "database/CPO_BRAIN.md"
JS_DATA = "database/dashboard_data.js"
CSV_PATH = 'cpo_master_ultimate.csv'
KNOWLEDGE_MD = 'KNOWLEDGE.md'

def generate_brain_from_master(master_path=MASTER_JSON):
    """
    Syncs the Authoritative JSON back to CSV, MD, and JS Dashboards.
    """
    if not os.path.exists(master_path):
        print(f"Error: {master_path} not found.")
        return

    with open(master_path, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    # 1. PREP CSV DATA (Sync JSON -> CSV with Valuation Tags)
    # We rebuild the CSV to ensure the 'Notes' column has the latest financials.
    header = ["Ticker", "Company", "Country", "Status", "Bucket", "Role", "Alpha Score", "Risk Adj", "Hiddenness", "Notes", "Monopoly Score", "Rev Growth Est", "Target Upside"]
    csv_rows = []
    
    for ticker, entry in master_data.items():
        res = entry.get("human_research", {})
        fin = entry.get("financials", {})
        
        # Build Valuation Tag for Notes
        price = fin.get('price', {}).get('regularMarketPrice', {}).get('raw', 0)
        mcap = fin.get('price', {}).get('marketCap', {}).get('raw', 0)
        pe = fin.get('summaryDetail', {}).get('trailingPE', {}).get('raw', 0)
        rev_growth = fin.get('financialData', {}).get('revenueGrowth', {}).get('raw', 0)
        
        val_tag = ""
        if mcap > 0:
            mcap_str = f"${mcap / 1e9:.2f}B"
            pe_str = f"{pe:.1f}x" if pe > 0 else "N/A"
            rev_str = f"{rev_growth*100:+.1f}%" if rev_growth else "N/A"
            val_tag = f"[ Val: {mcap_str} | P/E: {pe_str} | Rev: {rev_str} @ ${price:.2f} ]"
        
        # Merge tag into notes
        notes = res.get("Notes", "")
        if val_tag:
            if "[ Val" in notes or "[ Valuation" in notes:
                notes = re.sub(r"\[ (Val|Valuation):.*? \]", val_tag, notes)
            else:
                notes = notes.strip() + " " + val_tag
        
        row = {h: res.get(h, "") for h in header}
        row["Notes"] = notes
        csv_rows.append(row)

    # Save CSV
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(csv_rows)

    # 2. GENERATE JSON BRAIN (Ecosystem wide)
    research_content = ""
    if os.path.exists(KNOWLEDGE_MD):
        with open(KNOWLEDGE_MD, 'r', encoding='utf-8') as f:
            research_content = f.read()

    brain_data = {
        "metadata": {
            "title": "CPO Intelligence Brain",
            "last_synced": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "owner": "Ray"
        },
        "ecosystem": master_data,
        "technical_knowledge_base": research_content
    }
    with open(BRAIN_JSON, 'w', encoding='utf-8') as f:
        json.dump(brain_data, f, indent=2)

    # 3. GENERATE MARKDOWN BRAIN
    with open(BRAIN_MD, 'w', encoding='utf-8') as f:
        f.write(f"# [FAST] CPO INTELLIGENCE BRAIN\n")
        f.write(f"**Last Sync**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 1. STRUCTURED ECOSYSTEM ({len(master_data)} Plays)\n\n")
        f.write("| Ticker | Market Cap | P/E | Rev Growth | Target |\n")
        f.write("|---|---|---|---|---|\n")
        for ticker, entry in master_data.items():
            fin = entry.get("financials", {})
            mcap = fin.get('price', {}).get('marketCap', {}).get('fmt', "N/A")
            pe = fin.get('summaryDetail', {}).get('trailingPE', {}).get('fmt', "N/A")
            rg = fin.get('financialData', {}).get('revenueGrowth', {}).get('fmt', "N/A")
            target = entry.get("human_research", {}).get("Target Upside", "N/A")
            f.write(f"| {ticker} | {mcap} | {pe} | {rg} | {target} |\n")

    # 4. GENERATE JS DATA BRIDGE (Rich Master Data)
    js_content = f"window.CPO_MASTER_DATA = {json.dumps(master_data)};\n"
    js_content += f"window.CPO_LAST_SYNC = '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}';"
    with open(JS_DATA, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"DATABASE SYNC COMPLETE.")
    print(f"Master: {master_path} -> CSV, MD, JS Dashboard updated.")

if __name__ == "__main__":
    generate_brain_from_master()