import json
import re
from pathlib import Path

import requests


def build_massive_bridge():
    print("[BRIDGE] Building Massive Symbol Bridge (S&P 500 + Russell 2000)...")
    mapping = {}  # Name -> Symbol

    # 1. Fetch S&P 500 (Wikipedia)
    try:
        print("  [1/2] Fetching S&P 500...")
        url_sp = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        r = requests.get(url_sp, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        rows = re.findall(r"<tr>(.*?)</tr>", r.text, re.DOTALL)
        for row in rows:
            cols = re.findall(r"<td.*?>(.*?)</td>", row, re.DOTALL)
            if len(cols) >= 2:
                ticker = re.sub(r"<.*?>", "", cols[0]).strip().replace(".", "-")
                name = re.sub(r"<.*?>", "", cols[1]).strip()
                clean_name = re.sub(
                    r" (Inc\.|Corp\.|Ltd\.|Co\.|Corporation|Incorporated|Common Stock)$",
                    "",
                    name,
                    flags=re.I,
                ).strip()
                mapping[name.upper()] = ticker.upper()
                mapping[clean_name.upper()] = ticker.upper()
                # Simplified common variant
                mapping[clean_name.split(" ")[0].upper()] = ticker.upper()
    except Exception as e:
        print(f"  [ERR] S&P fetch fail: {e}")

    # 2. Fetch Russell 2000 (iShares CSV)
    try:
        print("  [2/2] Fetching Russell 2000 (IWM Holdings)...")
        # Direct Ajax CSV URL for IWM
        url_r2k = "https://www.ishares.com/us/products/239710/ishares-russell-2000-etf/1467271812596.ajax?fileType=csv&fileName=IWM_holdings&dataType=fund"
        r = requests.get(url_r2k, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)

        lines = r.text.split("\n")
        found_header = False
        for line in lines:
            if "Ticker" in line and "Name" in line:
                found_header = True
                continue
            if not found_header:
                continue

            # Simple CSV split (handling basic quotes)
            parts = line.split(",")
            if len(parts) >= 2:
                ticker = parts[0].strip().replace('"', "")
                name = parts[1].strip().replace('"', "")
                if not ticker or len(ticker) > 6 or "-" in ticker or ticker.isdigit():
                    continue

                clean_name = re.sub(
                    r" (Inc\.|Corp\.|Ltd\.|Co\.|Corporation|Incorporated|Common Stock)$",
                    "",
                    name,
                    flags=re.I,
                ).strip()
                # Update but don't overwrite S&P (S&P has higher authority for mapping collisions)
                if name.upper() not in mapping:
                    mapping[name.upper()] = ticker.upper()
                if clean_name.upper() not in mapping:
                    mapping[clean_name.upper()] = ticker.upper()
    except Exception as e:
        print(f"  [ERR] Russell fetch fail: {e}")

    # Standard Overrides
    mapping["GOOGLE"] = "GOOGL"
    mapping["ALPHABET"] = "GOOGL"
    mapping["NVIDIA"] = "NVDA"
    mapping["META"] = "META"
    mapping["FACEBOOK"] = "META"
    mapping["TESLA"] = "TSLA"
    mapping["APPLE"] = "AAPL"
    mapping["AMAZON"] = "AMZN"
    mapping["MICROSOFT"] = "MSFT"

    # Save
    root = Path(__file__).parent.parent
    db_path = root / "database" / "ticker_name_map.json"
    db_path_js = root / "database" / "ticker_name_map.js"

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
    with open(db_path_js, "w", encoding="utf-8") as f:
        f.write(f"const TICKER_NAME_MAP = {json.dumps(mapping, indent=2)};\n")
        f.write("if (typeof module !== 'undefined') module.exports = TICKER_NAME_MAP;")

    print(f"[OK] Bridge Expanded. {len(mapping)} mappings anchored.")
    return True


if __name__ == "__main__":
    build_massive_bridge()
