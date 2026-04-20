import json, re
from pathlib import Path

# Load Master Tickers for surgical precision
def get_master_tickers():
    try:
        master_path = Path("database/CPO_MASTER_DATA.json")
        if master_path.exists():
            data = json.loads(master_path.read_text(encoding="utf-8"))
            return set(data.keys())
    except:
        pass
    # Fallback to key known tickers if file missing
    return {"PGY", "NVDA", "DELL", "MSFT", "AAPL", "OSS", "VLN", "SOI", "TSEM", "AAOI", "COHR", "LITE", "POET", "SIVE", "IQE", "MRVL", "FN", "AEHR", "FORM", "BESI", "CIEN", "AXTI", "KEYS", "ALMU", "LWLG", "XNDU"}

MASTER_TICKERS = get_master_tickers()

def ultimate_reconstruct_v12_2(text):
    if not text: return ""
    
    # Standardize
    text = text.replace('\xa0', ' ').replace('\t', ' ')
    
    # 1. Handle handles (@Ph o t o n C a p -> @PhotonCap)
    def fix_handle(m):
        raw = m.group(0)
        if " " in raw and len(raw.replace(" ","")) > 3:
            return raw.replace(" ", "")
        return raw
    text = re.sub(r'(@[A-Za-z0-9\s_]{2,30})', fix_handle, text)

    # 2. Pre-standardize spaces after $ ($ NVDA -> $NVDA)
    text = re.sub(r'\$\s+', '$', text)
    
    # 3. Whitelist-first sliding window (CASE PRESERVING)
    res = ""
    i = 0
    while i < len(text):
        if text[i] == '$':
            # Space before $
            if res and res[-1] not in " ([\n\t": res += " "
            res += "$"
            i += 1
            
            potential_str = ""
            best_match_ticker = ""
            best_k = i
            
            # Look ahead up to 15 chars for the "Ticker Zone"
            for k in range(i, min(i + 15, len(text))):
                char = text[k]
                if char.isalnum() or char.isspace() or char in "/.":
                    potential_str += char
                    # Compare upper, ignoring spaces and slashes
                    clean_upper = potential_str.upper().replace(" ", "").replace("/", "").replace(".", "")
                    if clean_upper in MASTER_TICKERS:
                        best_match_ticker = clean_upper
                        best_k = k + 1
                    # Price protection: $10.60
                    if re.match(r'^\d', potential_str) and "." in potential_str:
                         pass 
                elif char == "$": break
                else: break
            
            if best_match_ticker:
                res += best_match_ticker
                i = best_k
            else:
                # Fallback: take until space or symbol
                match = re.match(r'^([A-Za-z0-9]{1,6})', text[i:])
                if match:
                    t_val = match.group(1)
                    if not t_val[0].isdigit():
                        res += t_val.upper()
                        i += len(t_val)
                    else:
                        res += t_val; i += len(t_val)
                else: pass
        else:
            res += text[i]; i += 1
    
    # Final cleanup: Detach from punctuation (except numbers)
    res = re.sub(r'(\$[A-Z0-9]{2,10})([.,!?%:])(?![0-9])', r'\1 \2', res)
    # Detach from lowercase words: $NVDAhello -> $NVDA hello
    res = re.sub(r'(\$[A-Z0-9]{2,10})([a-z]{2,})', r'\1 \2', res)
    # Detach common smashed words (Upper)
    res = re.sub(r'(\$[A-Z0-9]{2,10})(WHICH|THAT|IS|WITH|FROM|AND|OF|OR|FOR|THE|TO)([A-Z]{1,})', r'\1 \2 \3', res)
    # Detach hyphens: $SGBAF-WORKS -> $SGBAF - WORKS
    res = re.sub(r'(\$[A-Z0-9]{2,10})-([A-Z]{2,})', r'\1 - \2', res)
    
    return re.sub(r' +', ' ', res).strip()

def process_translation(text):
    if not text: return text
    # Detect foreign chars
    if re.search(r'[\u3040-\u30ff\u4e00-\u9faf\uac00-\ud7af]', text):
        if "[EN:" in text: return text
        
        # known manual fixes
        mapping = {
            "학위할때 포토닉스가 신생이기도했고 먼 미래 기술이라 생각했는데 졸업하고 마침 직장을 잡고보니 뜨고있는 것 같아 운이 좋다고 생각합니다. ㅎㅎ 말씀 감사드립니다": 
            "When I was getting my degree, photonics was new and I thought it was a technology of the far future. After graduating and getting a job, it seems to be taking off, so I think I'm lucky. Haha, thank you for your words",
            "あなたのコミュニティとサブスクリプションはとても専門的で勉強になるので、日本の投資家の皆さんにも、ぜひ紹介したいです":
            "Your community and subscription are so professional and educational that I would love to introduce them to Japanese investors.",
            "섭스택에서 정말 잘 먹힐 것 같아서, 강력히 권유했는데, 정말 놀라울 정도로 빠르게 성장하셨습니다. 항상 유익할 글과 흥미로운 글 재밌게 잘 써주시는 담낭님 Kudos!!":
            "I strongly recommended it because I thought it would do really well on Substack, and you have grown surprisingly fast. Thank you for always writing such informative and interesting posts, Dam-nang-nim! Kudos!!"
        }
        for k, v in mapping.items():
            if k in text:
                return f"[EN: Translation] {v} (Original: {text})"
        
        return f"[FOREIGN TEXT] {text}"
    return text

def run_repair():
    print("V12.2 SURGICAL SCALPEL - DATA INTEGRITY")
    db_path = Path("database")
    files = ["x_intel_aleabitoreddit.json", "x_intel_PhotonCap.json", "x_intel_KawzInvests.json"]
    
    history_log = []
    
    for fname in files:
        f = db_path / fname
        if not f.exists(): continue
        print(f"Processing {fname}...")
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            local_fixes = 0
            for item in data:
                old = item.get("text", "")
                
                # 1. Ticker Fix
                new = ultimate_reconstruct_v12_2(old)
                
                # 2. Translation Fix
                new = process_translation(new)
                
                if old != new:
                    item["text"] = new
                    local_fixes += 1
                    history_log.append(f"[{fname}] ID: {item.get('id', 'N/A')}\n  OLD: {old}\n  NEW: {new}\n")
            
            if local_fixes > 0:
                f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"  Fixed {local_fixes} posts in {fname}.")
        except Exception as e:
            print(f"  Error processing {fname}: {e}")
            
    if history_log:
        Path("engine/repair_history_v12_2.txt").write_text("\n".join(history_log), encoding="utf-8")
        print(f"Detailed repair log written to engine/repair_history_v12_2.txt")

if __name__ == "__main__":
    run_repair()