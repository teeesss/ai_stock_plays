import json
import re
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# engine/repair_tickers.py
# V13.1 — Safe Forensic Repair Bridge
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"

def forensic_repair(text: str) -> str:
    if not text: return ""
    def collapse_fragment(m):
        return m.group(0).replace(" ", "")
    
    # 1. Collapse fragmented chains: $ N V D A or S U P P L Y
    text = re.sub(r'[A-Z](?:\s[A-Z]\b)+', collapse_fragment, text)
    text = re.sub(r'\$[A-Z](?:\s[A-Z]\b)+', collapse_fragment, text)
    
    # 2. Add spaces between smashed tickers ($PGY$NVDA -> $PGY $NVDA)
    text = re.sub(r'(\$[A-Z0-9]{2,10})(\$[A-Z0-9])', r'\1 \2', text)
    
    # 3. Separate @Handles (@PhotonCapis -> @PhotonCap is)
    text = re.sub(r'(@[A-Za-z0-9_]{1,20})([A-Za-z])', r'\1 \2', text)

    # 4. Remove obvious $ mistakes from common words
    for word in ["SUPPLY", "SUPPORT", "SUCCESS", "SOURCE", "SMALL", "SERVICE", "SYSTEM", "SWITCH"]:
        text = re.sub(rf'\${word}', word.lower(), text, flags=re.IGNORECASE)

    return re.sub(r'\s+', ' ', text).strip()

def repair_user(username: str):
    user_file = DB_DIR / f"x_intel_{username}.json"
    if not user_file.exists(): return
    
    try:
        posts = json.loads(user_file.read_text(encoding="utf-8"))
        for p in posts:
            p["text"] = forensic_repair(p.get("text", ""))
        user_file.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
    except: pass

if __name__ == "__main__":
    for user in ["aleabitoreddit", "PhotonCap", "KawzInvests"]:
        repair_user(user)
