import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"
USERS = ["aleabitoreddit", "PhotonCap", "KawzInvests"]

def deep_repair_text(text: str) -> str:
    if not text:
        return ""
    
    # Rationale: Any $TICKER followed by a space and 1-3 uppercase letters
    # is almost certainly a Nitter-split fragment in this dataset.
    # We loop until no more merges can be made (to handle $A B C D)
    
    count = 0
    while True:
        # Match $ + uppercase + space + (1-3 uppercase letters) + non-lowercase bound
        # The lookahead (?![a-z]) ensures we don't merge into words like "$AMD is"
        new_text = re.sub(r'\$([A-Z0-9]{1,15})\s([A-Z0-9]{1,3})(?![a-z0-9])', r'$\1\2', text)
        if new_text == text:
            break
        text = new_text
        count += 1
        if count > 10: break # safety
        
    # Also catch $ T I C K E R (where first letter is split)
    while True:
        new_text = re.sub(r'\$\s([A-Z0-9])', r'$\1', text)
        if new_text == text:
            break
        text = new_text
        
    # Final cleanup of spacing
    text = re.sub(r'([a-zA-Z0-9])([\$@])', r'\1 \2', text)
    text = re.sub(r'(\$[A-Z]{2,10})([a-zA-Z0-9])', r'\1 \2', text)
    text = re.sub(r'  +', ' ', text).strip()
    
    return text

def run_repair():
    print("="*60)
    print("ULTIMATE TICKER RECONSTRUCTION V8.9")
    print("="*60)
    
    # Ticker fragment detection for auditing
    # Matches $... followed by space then some letters (up to 3) followed by boundary
    SPLIT_AUDIT = re.compile(r'\$[A-Z0-9]{1,15}\s[A-Z0-9]{1,3}(?![a-z0-9])')

    for user in USERS:
        f = DB_DIR / f"x_intel_{user}.json"
        if not f.exists(): continue
        
        posts = json.loads(f.read_text(encoding="utf-8"))
        
        before = sum(1 for p in posts if SPLIT_AUDIT.search(p.get("text", "")))
        
        repaired = 0
        for p in posts:
            orig = p.get("text", "")
            fixed = deep_repair_text(orig)
            if fixed != orig:
                p["text"] = fixed
                repaired += 1
        
        after = sum(1 for p in posts if SPLIT_AUDIT.search(p.get("text", "")))
        f.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
        
        print(f"@{user}: Artifacts {before} -> {after} | Fixed {repaired} posts")

if __name__ == "__main__":
    run_repair()