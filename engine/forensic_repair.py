import json
import re
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# V13.2 ULTIMATE FORENSIC RECOVERY
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"

# Expanded dictionary of common corrupted phrases from the rogue repair
CLEANUP_MAP = {
    "NVDACPOSUPP ly": "NVDA CPO supply",
    "NVDACPOSUP P ly": "NVDA CPO supply",
    "$NVDACPOSUPP ly": "NVDA CPO supply",
    "andGOTAFR ee": "and got a free",
    "MRVLANDGOTAF R ee": "MRVL and got a free",
    "MRVLANDGOTAFR ee": "MRVL and got a free",
    "TSMCOUPEfor": "TSMC OUP for", # Or whatever TSM OUP was
    "METAOP tical": "META optical",
    "BKKTAN D": "BKKT and",
    "ASSTTH E": "ASST they",
    "LAS R": "laser",
    "EO S.AX": "EOS.AX",
    "OPT X": "OPTX",
    "CitronRese a r c h": "Citron Research",
    "NVDARTXPR O4500B lackwell": "NVDA RTX PRO 4500 Blackwell",
    "DELLP owerEdge": "DELL PowerEdge",
    "NOK O ptical": "NOK Optical",
    "NVD A": "NVDA",
    "TH ey": "they",
    "COINISP R obably": "COIN is probably",
}

def forensic_repair_v13_2(text: str) -> str:
    if not text: return ""

    # 1. Direct phase-literal replacement
    for bad, good in CLEANUP_MAP.items():
        text = text.replace(bad, good)
        text = text.replace("$" + bad, good)

    # 2. Letter-by-letter collapse ($ N V D A -> $NVDA)
    def collapse_fragment(m):
        return m.group(0).replace(" ", "")
    text = re.sub(r'\$[A-Z](?:\s[A-Z]\b)+', collapse_fragment, text)
    text = re.sub(r'[A-Z](?:\s[A-Z]\b)+', collapse_fragment, text)

    # 3. Handle common smashed word pattern: $TICKERword
    # $NVDAis -> $NVDA is
    for t in ["NVDA", "TSMC", "MRVL", "GOOGL", "META", "AAPL", "COIN", "BKKT", "ASST", "NOK", "DELL", "SMCI", "CIEN", "AAOI", "POET"]:
        text = re.sub(rf'(\${t})([a-z]{{2,}})', r'\1 \2', text)
        text = re.sub(rf'({t})([a-z]{{2,}})', r'\1 \2', text) # Untagged but smashed

    # 4. Final Spacing
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def run_repair():
    print("Initiating V13.2 Ultimate Forensic Repair...")
    files = list(DB_DIR.glob("x_intel_*.json"))
    for f in files:
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
            posts = raw if isinstance(raw, list) else raw.get("posts", [])
            for p in posts:
                p["text"] = forensic_repair_v13_2(p.get("text", ""))
            f.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  [{f.name}] Repaired.")
        except: pass

if __name__ == "__main__":
    run_repair()