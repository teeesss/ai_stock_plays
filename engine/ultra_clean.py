import json, re, sys
from pathlib import Path

def ultra_clean(text):
    if not text: return ""
    
    # 1. Join any $ followed by Uppercase chars and spaces, recursively
    # This covers $M R V L, $MRV L, $AA O I, etc.
    while True:
        # Match $ + (any caps/nums) + (space) + (1-2 caps/nums)
        # The positive lookahead (?![a-z]) ensures we don't eat words
        new = re.sub(r'(\$[A-Z0-9]+)\s([A-Z0-9]{1,2})(?![a-z])', r'\1\2', text)
        if new == text: break
        text = new
    
    # 2. Handle the "space after $" case: $ N V D A
    while True:
        new = re.sub(r'\$\s+([A-Z0-9])', r'$\1', text)
        if new == text: break
        text = new

    # 3. Handle ticker sequences with dots: $LP K.DE
    text = re.sub(r'(\$[A-Z0-9]+)\s([A-Z0-9]\.[A-Z]{2})', r'\1\2', text)

    # 4. Final Spacing Refinement
    # Space before $ if preceded by alpha
    text = re.sub(r'([a-zA-Z0-9])([\$@])', r'\1 \2', text)
    # Space after ticker if followed by word
    text = re.sub(r'(\$[A-Z0-9]{2,12})([a-zA-Z])', r'\1 \2', text)
    # Ensure no double spaces
    text = re.sub(r'  +', ' ', text).strip()
    
    return text

def run():
    print("ULTRA-SURGICAL CLEAN V9.2")
    for user in ["aleabitoreddit", "PhotonCap", "KawzInvests"]:
        f = Path(f"database/x_intel_{user}.json")
        if not f.exists(): continue
        data = json.loads(f.read_text(encoding="utf-8"))
        
        fixed = 0
        for p in data:
            o = p.get("text", "")
            n = ultra_clean(o)
            if o != n:
                p["text"] = n
                fixed += 1
        
        f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"@{user}: Repaired {fixed} posts.")

if __name__ == "__main__":
    run()