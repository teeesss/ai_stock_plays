import json, re, sys
from pathlib import Path

# Use the V10.1 Ironclad logic
def ironclad_reconstruct(text):
    if not text: return ""
    
    # 1. Pre-process: Handle lowercase ticker split fragments
    def upper_tickers(m):
        return m.group(0).upper()
    text = re.sub(r'\$[a-z]{1,4}(?:\s[a-z]{1,2})*', upper_tickers, text)

    # 2. Split into segments starting with $
    segments = re.split(r'(?=\$)', text)
    reconstructed_segments = []
    
    for seg in segments:
        if not seg.startswith('$'):
            reconstructed_segments.append(seg)
            continue
        
        # Match $ + Ticker Zone (Caps/Nums/Spaces) + Remainder
        match = re.search(r'^\$([A-Z0-9\s]+)(.*)', seg)
        if match:
            ticker_zone, remainder = match.group(1), match.group(2)
            clean_ticker = ticker_zone.replace(" ", "")
            
            if remainder and remainder[0].islower():
                remainder = " " + remainder
            
            reconstructed_segments.append(f"${clean_ticker}{remainder}")
        else:
            reconstructed_segments.append(seg)
            
    result = "".join(reconstructed_segments)
    
    # 3. Recursively add spaces between smashed tickers
    while True:
        new_result = re.sub(r'(\$[A-Z0-9]{2,10})(\$[A-Z0-9])', r'\1 \2', result)
        if new_result == result:
            break
        result = new_result
    
    # 4. Final Spacing Refinement
    result = re.sub(r'([a-z0-9])([\$@])', r'\1 \2', result)
    result = re.sub(r'(\$[A-Z0-9]{2,12})([a-zA-Z])', r'\1 \2', result)
    return re.sub(r'\s+', ' ', result).strip()

def run():
    print("V10.1 IRONCLAD GLOBAL REPAIR")
    users = ["aleabitoreddit", "PhotonCap", "KawzInvests"]
    for u in users:
        f = Path(f"database/x_intel_{u}.json")
        if not f.exists(): continue
        data = json.loads(f.read_text(encoding="utf-8"))
        count = 0
        for p in data:
            old = p.get("text", "")
            new = ironclad_reconstruct(old)
            if old != new:
                p["text"] = new
                count += 1
        f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"@{u}: Ironclad Repaired {count} posts.")

if __name__ == "__main__":
    run()
