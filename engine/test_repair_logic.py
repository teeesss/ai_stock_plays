import re

def ultimate_reconstruct(text):
    if not text: return ""
    
    # 0. Standardize Whitespace
    text = text.replace('\xa0', ' ').replace('\t', ' ')
    
    # 1. Pre-standardize: insert space before all $ for easier parsing
    # But only if not already preceded by space or start of string
    text = re.sub(r'([A-Za-z0-9])\$', r'\1 $', text)
    
    # 2. The Atomic Merger
    def merge_logic(match):
        raw = match.group(0)
        # We need to be careful with things like "$PG Y$NVD A"
        # Let's split by space
        parts = raw.split(' ')
        res = parts[0]
        
        for i in range(1, len(parts)):
            p = parts[i]
            if not p: continue
            
            # If the part contains a $, it might be a smashed ticker start
            if '$' in p:
                # e.g. "Y$NVDA" -> split into "Y" and "$NVDA"
                sub_parts = p.split('$')
                # sub_parts[0] is the fragment "Y"
                # sub_parts[1] is "NVDA"
                frag = sub_parts[0]
                if len(frag) <= 2:
                    res += frag
                    # Rest is a new ticker start
                    remainder = "$" + "$".join(sub_parts[1:]) + " " + " ".join(parts[i+1:])
                    return res.upper() + " " + remainder.strip()
                else:
                    # Too long to be a fragment?
                    return res.upper() + " " + " ".join(parts[i:])

            # Check for fragment with trailing word: "Lhello" -> "L" part of ticker, "hello" not
            m = re.match(r'^([A-Za-z0-9]{1,2})([a-z].*)', p)
            if m:
                head, tail = m.group(1), m.group(2)
                res += head
                remainder = tail + " " + " ".join(parts[i+1:])
                return res.upper() + " " + remainder.strip()
            
            # Check for fragment with trailing symbol: "Y/hello" -> "Y" part of ticker
            ms = re.match(r'^([A-Za-z0-9]{1,2})([/.,!?].*)', p)
            if ms:
                head, tail = ms.group(1), ms.group(2)
                res += head
                remainder = tail + " " + " ".join(parts[i+1:])
                return res.upper() + " " + remainder.strip()

            # Normal fragment: short
            if len(p) <= 2:
                res += p
            elif p.isupper() and len(p) <= 4:
                res += p
            else:
                # Real word
                return res.upper() + " " + " ".join(parts[i:])
        
        return res.upper()

    # Run multiple times to catch overlapping split chains
    for _ in range(5):
        text = re.sub(r'\$[A-Za-z0-9]+(?: +[A-Za-z0-9][A-Za-z0-9_a-z/.,!$?]*)+', merge_logic, text)

    # 3. Separate Smashed Tickers (No space between them)
    for _ in range(5):
        text = re.sub(r'(\$[A-Z0-9]{2,10})(\$[A-Z0-9])', r'\1 \2', text)
    
    # 4. Detach Trailing Words
    text = re.sub(r'(\$[A-Z0-9]{2,10})([a-z])', r'\1 \2', text)
    
    # 5. Detach Symbols
    text = re.sub(r'(\$[A-Z0-9]{2,10})([/.,!?])', r'\1 \2', text)

    # 6. Final Cleanup
    return re.sub(r' +', ' ', text).strip()

scenarios = [
    "$PG Y$NVD A$DELL $MS FT$AAP Lhello",
    "$PG Y$NVD Ahello",
    "$P GY $NV DAhello",
    "$P GY$NVD A hellowhatisgoingon",
    "$PGY$NVD Ahello",
    "$PGY$NVDAhelllo",
    "$PGY$NVD A/hello",
    "$PG Y$NVD A$DELL $MS/FT$AAP Lhello",
    "$PG Y/$NVD Ahello",
    "$P GY $NV DA/hello",
    "$pg y$nv dahello",
    "$pgy$nvdahello",
    "$pg y$nv dahello",
    "$pg y$nv da$de ll$ap pl",
    "$pg y$nv da$de ll/$ap pl"
]

if __name__ == "__main__":
    for s in scenarios:
        print(f"IN:  {s}")
        print(f"OUT: {ultimate_reconstruct(s)}")
        print("-" * 20)