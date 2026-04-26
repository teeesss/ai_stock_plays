import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"


def final_reconstruct(text):
    if not text:
        return ""
    # Use the proven debug logic: match greedily and strip spaces
    # Matches $ followed by a sequence of letters and spaces that are single-caps
    # Or fragment + single-caps.
    # Pattern: $ + CAPS + 1 or more (SPACE + SINGLE CAP + BOUNDARY)

    # Pass 1: Handle $PG Y, $AA O I
    text = re.sub(r"\$[A-Z0-9]+(?:\s[A-Z0-9]\b)+", lambda m: m.group(0).replace(" ", ""), text)

    # Pass 2: Handle $ N V D A
    text = re.sub(r"\$[A-Z0-9](?:\s[A-Z0-9]\b)+", lambda m: m.group(0).replace(" ", ""), text)

    # Pass 3: Catch any remaining $TICKER SPACE CAPS (1-2 chars)
    # e.g. $NVDACP O
    text = re.sub(r"\$([A-Z0-9]{2,10})\s([A-Z0-9]{1,2})\b", r"$\1\2", text)

    # Final spacing cleanup
    text = re.sub(r"([a-zA-Z0-9])([\$@])", r"\1 \2", text)
    text = re.sub(r"(\$[A-Z0-9]{2,12})([a-zA-Z0-9])", r"\1 \2", text)
    text = re.sub(r"  +", " ", text).strip()
    return text


def clean_all():
    print("Zero-Issue Ticker Repair V9.0")
    AUDIT = re.compile(r"\$[A-Z0-9]{1,15}\s[A-Z0-9]{1,3}(?![a-z0-9])")

    for user in ["aleabitoreddit", "PhotonCap", "KawzInvests"]:
        f = DB_DIR / f"x_intel_{user}.json"
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))

        repaired = 0
        for p in data:
            old = p.get("text", "")
            new = final_reconstruct(old)
            if old != new:
                p["text"] = new
                repaired += 1

        f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        remaining = sum(1 for p in data if AUDIT.search(p.get("text", "")))
        print(f"@{user}: Repaired {repaired} | Remaining Artifacts: {remaining}")


if __name__ == "__main__":
    clean_all()
