import json, re, sys
from pathlib import Path

# The Definitive Repair Pattern
def repair_text_final(text):
    if not text: return ""
    
    # 1. Match anything starting with $ followed by ONLY Uppercase/Numbers/Spaces, 
    # but the sequence MUST contain at least one space and end with an Uppercase/Number.
    # This prevents eating normal spaces in sentences while joining ticker splits.
    def merger(m):
        return m.group(0).replace(" ", "")
    
    # Pattern: $ then 1+ [A-Z0-9] then (1 or more chunks of [space + 1-2 [A-Z0-9]])
    # Example: $OS S, $PG Y, $N V D A, $AAOI O
    text = re.sub(r'\$[A-Z0-9]{1,10}(?:\s[A-Z0-9]{1,2})+', merger, text)
    
    # 2. Case where it starts with space after $: $ N V D A
    text = re.sub(r'\$\s+[A-Z0-9]', lambda m: m.group(0).replace(" ", ""), text)
    
    # 3. Space cleanup
    text = re.sub(r'([a-zA-Z0-9])([\$@])', r'\1 \2', text)
    text = re.sub(r'(\$[A-Z0-9]{2,12})([a-zA-Z0-9\:])', r'\1 \2', text)
    text = re.sub(r'  +', ' ', text).strip()
    return text

def execute():
    users = ["aleabitoreddit", "PhotonCap", "KawzInvests"]
    for u in users:
        f = Path(f"database/x_intel_{u}.json")
        if not f.exists(): continue
        data = json.loads(f.read_text(encoding="utf-8"))
        count = 0
        for p in data:
            old = p.get("text", "")
            new = repair_text_final(old)
            if old != new:
                p["text"] = new
                count += 1
        f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"@{u}: Repaired {count} posts")

if __name__ == "__main__":
    execute()
