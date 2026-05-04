import json
import re
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# engine/repair_tickers.py
# V13.1 - Safe Forensic Repair Bridge
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"


def forensic_repair(text: str) -> str:
    if not text:
        return ""

    # 1. Collapse single-letter chains starting with $ ($ N V D A -> $NVDA)
    text = re.sub(r"\$[A-Z](?:\s[A-Z]\b)+", lambda m: m.group(0).replace(" ", ""), text)

    # 2. Collapse fragments after a multi-letter ticker ($AA O I -> $AAOI)
    text = re.sub(
        r"\$([A-Z]{2,5})\s([A-Z]\b(?:\s[A-Z]\b)*)",
        lambda m: "$" + m.group(1) + m.group(2).replace(" ", ""),
        text,
    )

    # 3. Collapse bare capital chains (C P O -> CPO)
    text = re.sub(r"(?<!\w)[A-Z](?:\s[A-Z]\b)+", lambda m: m.group(0).replace(" ", ""), text)

    # Rule 1: Fix smashed tickers ($AAOI -> $AAOI)
    # This rule looks for non-whitespace characters followed by '$' and adds a space
    # It now includes a broader range of characters (including foreign ones)
    text = re.sub(r"([^\s$])(\$)", r"\1 \2", text)

    # Rule 2: Fix specific cases where tickers are concatenated with numbers or words
    # e.g., "1.$AAOI" -> "1. $AAOI"
    text = re.sub(r"(\d+)\.(\$)", r"\1. \2", text)

    # 5. Final Spacing Refinement
    text = re.sub(r"([a-z0-9])([\$@])", r"\1 \2", text)  # Space before $ or @
    text = re.sub(r"(\$[A-Z0-9]{2,12})([a-z]{2,})", r"\1 \2", text)  # $NVDAis -> $NVDA is

    # 6. Separate @Handles (@PhotonCapis -> @PhotonCap is)
    text = re.sub(r"(@[A-Za-z0-9_]{1,20})([A-Za-z])", r"\1 \2", text)

    # 7. Remove obvious $ mistakes from common words
    for word in [
        "SUPPLY",
        "SUPPORT",
        "SUCCESS",
        "SOURCE",
        "SMALL",
        "SERVICE",
        "SYSTEM",
        "SWITCH",
    ]:
        text = re.sub(rf"\${word}", word.lower(), text, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", text).strip()


def repair_user(username: str):
    user_file = DB_DIR / f"x_intel_{username}.json"
    if not user_file.exists():
        return

    try:
        posts = json.loads(user_file.read_text(encoding="utf-8"))
        modified = False
        for p in posts:
            old_text = p.get("text", "")
            new_text = forensic_repair(old_text)
            if old_text != new_text:
                p["text"] = new_text
                modified = True

        if modified:
            user_file.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"Error repairing {username}: {e}")


if __name__ == "__main__":
    for f in DB_DIR.glob("x_intel_*.json"):
        if f.name == "x_intel_master.json":
            continue
        user = f.name.replace("x_intel_", "").replace(".json", "")
        print(f"Repairing @{user}...")
        repair_user(user)
