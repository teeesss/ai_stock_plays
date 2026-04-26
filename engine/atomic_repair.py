import json
from pathlib import Path


# THE ATOMIC HAMMER V11.0
def atomic_ticker_join(text):
    if not text:
        return ""

    # 1. Standardize all whitespace to normal spaces first
    text = text.replace("\xa0", " ").replace("\t", " ")

    # 2. Match $ followed by ANYTHING until the next boundary that looks like a word
    # Split by whitespace, then join the parts that were split
    words = text.split(" ")
    fixed_words = []

    i = 0
    while i < len(words):
        w = words[i]
        if w.startswith("$") and len(w) <= 10:
            # Check if NEXT word is a single or double CAPS fragment
            # e.g. $PG Y
            while i + 1 < len(words) and len(words[i + 1]) <= 2 and words[i + 1].isupper():
                w += words[i + 1]
                i += 1
            # Special case for $ N V D A
            if len(w) == 1:  # just $
                while i + 1 < len(words) and len(words[i + 1]) == 1 and words[i + 1].isupper():
                    w += words[i + 1]
                    i += 1
            fixed_words.append(w)
        else:
            fixed_words.append(w)
        i += 1

    result = " ".join(fixed_words)

    # 3. Final safety: Remove any internal spaces in known broken patterns
    patterns = [
        ("$OS S", "$OSS"),
        ("$VL N", "$VLN"),
        ("$PG Y", "$PGY"),
        ("$PO E T", "$POET"),
        ("$POE T", "$POET"),
        ("$NVD A", "$NVDA"),
        ("$MRV L", "$MRVL"),
        ("$JB L", "$JBL"),
        ("$MS F T", "$MSFT"),
    ]
    for old, new in patterns:
        result = result.replace(old, new)

    return result


def run():
    print("V11.0 ATOMIC HAMMER REPAIR")
    users = ["aleabitoreddit", "PhotonCap", "KawzInvests"]
    for u in users:
        p = Path(f"database/x_intel_{u}.json")
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        fixes = 0
        for item in data:
            old = item.get("text", "")
            new = atomic_ticker_join(old)
            if old != new:
                item["text"] = new
                fixes += 1
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"@{u}: Atomic Repaired {fixes} posts.")


if __name__ == "__main__":
    run()
