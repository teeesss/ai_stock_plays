"""
forensic_repair_v14.py
======================
V14 COMPREHENSIVE FORENSIC REPAIR
Addresses ALL known corruption patterns found in the database:
  1. $TICKER word (letter-by-letter Nitter splits)
  2. $TICKERword (smashed: $COinisProb -> $COIN is prob)
  3. $TI CKE R (multi-fragment splits with mid-word breaks)
  4. @Handle fragmentation (@Ph o t o n C a p)

Run this BEFORE rebuild_master to ensure clean data.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"

# ─────────────────────────────────────────────────────────────
# KNOWN TICKER UNIVERSE (confirmed real tickers we care about)
# ─────────────────────────────────────────────────────────────
KNOWN_TICKERS = {
    # CPO Core
    "NVDA", "AVGO", "MRVL", "TSMC", "AAPL", "MSFT", "GOOGL", "META", "AMZN",
    # Lasers / Photonics
    "LITE", "COHR", "SIVE", "SIVEF", "AAOI", "IQE", "AXTI", "POET", "LWLG",
    # OSAT / Packaging
    "ASX", "AMKR", "FN", "CLS",
    # Bonding / Equipment
    "BESIY", "KLIC", "ASMPT", "MYCRF", "TWCPY", "DSCSY",
    # Substrates
    "IBIEY", "DNPCY", "SOI", "TSEM", "GFS",
    # Testing
    "ONTO", "CAMT", "NVMI", "FORM", "AEHR", "COHU", "KLAC",
    # Chemicals / Materials
    "ENTG", "SHWDY", "MTRN", "ASMIY", "ASMVY",
    # Connectivity
    "CRDO", "APH", "GLW",
    # Equipment
    "VECO", "AIXNY", "MKSI", "NDSN", "NOVT",
    # ETFs
    "XSD", "SMH", "SOXX", "PTF",
    # Crypto / Other (commonly mentioned)
    "COIN", "SOFI", "BKKT", "ASST", "IREN", "NBIS", "RDDT", "SNAP",
    # Other stocks mentioned in posts
    "NVMI", "HPS", "ALRIB", "VIRT", "SNDK", "INTU", "PYPL", "HOOD",
    "HPSA",  # HPS.A
    "AXTI",  # AXT Inc
    "LITE", "COHR",
    "SMTOY", "AIXA", "AIXTRON",
    "CRCL", "CRCLST",
    "BKKT", "ASST", "IREN", "NBIS",
    "PGY", "OSS", "VLN",
}

# ─────────────────────────────────────────────────────────────
# SURGICAL PATTERN MAP: (bad_pattern → correct_text)
# These are exact string replacements for known corruptions
# ─────────────────────────────────────────────────────────────
EXACT_FIXES = {
    # Crypto / Finance posts corruption
    "$CO inisPR obably": "$COIN is probably",
    "$CO inisP R obably": "$COIN is probably",
    "$CRCLST ablecoins": "$CRCL stablecoins",
    "$CRCLST able": "$CRCL stable",
    "$NB isLA st": "$NBIS last",
    "$NB is": "$NBIS",
    "$IREN,NO t": "$IREN, not",
    "$IREN,not": "$IREN, not",
    "$BKKT and$ASST": "$BKKT and $ASST",
    "ANDTH is": "AND this",
    "andTH is": "and this",
    "andGOTAFR ee": "and got a free",
    "MRVLANDGOTAFR ee": "MRVL and got a free",

    # NVDA/CPO smashing
    "$NV D A": "$NVDA",
    "$NV D": "$NVD",
    "NV D A": "NVDA",
    "$NVDACPO": "$NVDA CPO",
    "NVDACPOSUPP ly": "NVDA CPO supply",

    # Meta/Google splits
    "$MR V L": "$MRVL",
    "$GO O G L": "$GOOGL",
    "$ME T A": "$META",
    "$TS M C": "$TSMC",
    "TSMC OUP": "TSMC OUP",  # keep as-is

    # Common word-smashes at ticker boundaries
    "$SOIforSU bstrates": "$SOI for substrates",
    "forSU bstrates": "for substrates",
    "forCA pex": "for Capex",
    "forCA": "for CA",
    "$RDDT/": "$RDDT /",
    "$SNAP areLI": "$SNAP are LI",
    "$inTUareGO ing": "$INTU are going",
    "inTUareGO ing": "INTU are going",

    # NBIS corruption
    "$NB isLA st year": "$NBIS last year",
    "$NB is last": "$NBIS last",

    # BKKT / ASST common corruptions
    "$BKKT and $ASST they": "$BKKT and $ASST they",
    "$ASST andTH": "$ASST and TH",  # TH is usually "this" or "they"
    "andTH": "and th",

    # PhotonCap handle repair
    "@Photo n C a p": "@PhotonCap",
    "@Ph o t o n C a p": "@PhotonCap",

    # Common word/number collision
    "$1B+WASPO ssible": "$1B+ was possible",
    "$3.8BwithLE ss": "$3.8B with less",
    "$IQEHADDE bt": "$IQE had debt",
    "$1B+WASPO": "$1B+ was po",
    "WASPO ssible": "was possible",
    "HADDE bt": "had debt",
    "withLE ss": "with less",

    # OpenAI / other
    "$122 B+forCA pex": "$122B+ for Capex",
    "B+forCA pex": "B+ for Capex",
    "forCA pex": "for Capex",
}

# ─────────────────────────────────────────────────────────────
# REGEX-BASED REPAIRS (applied after exact fixes)
# ─────────────────────────────────────────────────────────────

def apply_regex_repairs(text: str) -> str:
    """Comprehensive regex-based ticket fragment repair."""
    if not text:
        return text

    # ── Step 1: Collapse letter-by-letter single-char splits
    # Matches: $N V D A -> $NVDA, $A A O I -> $AAOI
    def collapse_dollar_fragment(m):
        return m.group(0).replace(" ", "")

    text = re.sub(r'\$[A-Z](?:\s[A-Z]){1,8}\b', collapse_dollar_fragment, text)

    # ── Step 2: Collapse non-dollar single-char chains (bare ALL-CAPS letter chains)
    # e.g. "N V D A" → "NVDA" (only when surrounded by appropriate context)
    # Be conservative: only collapse if all tokens are single uppercase letters
    def collapse_bare_fragment(m):
        return m.group(0).replace(" ", "")
    text = re.sub(r'(?<!\w)[A-Z](?:\s[A-Z]){2,7}(?!\w)', collapse_bare_fragment, text)

    # ── Step 3: Fix $TICKERword smashing (ticker immediately followed by lowercase word)
    # e.g. $NVDAis -> $NVDA is, $COINis -> $COIN is
    # Only trigger if followed by 3+ lowercase chars (avoids false positives on $NVDAx)
    text = re.sub(r'(\$[A-Z]{2,8})([a-z]{2,})', r'\1 \2', text)

    # ── Step 4: Fix $TICKERWord smashing (ticker followed by uppercase continuation)
    # e.g. $TSMCOUPfor -> $TSMC OUP for
    # Careful: only break if the uppercase suffix looks like a word (3+ chars)
    text = re.sub(r'(\$[A-Z]{3,8})([A-Z]{3,}[a-z]{2,})', r'\1 \2', text)

    # ── Step 5: Fix partial ticker then lowercase continuation
    # e.g. "$CO inisPR obably" patterns after exact fixes: "PR obably" -> "probably"
    text = re.sub(r'([A-Z]{2,})\s([a-z]{2,})', lambda m: m.group(1).lower() + m.group(2)
                  if len(m.group(1)) <= 3 and m.group(1) not in KNOWN_TICKERS
                  else m.group(0), text)

    # ── Step 6: Fix smashed @handles (@Photo n C a p -> @PhotonCap)
    # Pattern: @ followed by mixed case/space chars that look like a handle
    def fix_handle(m):
        raw = m.group(0)
        # If it has spaces and all parts are short (1-3 chars), it's likely fragmented
        parts = raw[1:].split(' ')
        if all(len(p) <= 3 for p in parts) and len(parts) > 2:
            return '@' + ''.join(parts)
        return raw
    text = re.sub(r'@[A-Za-z0-9](?:\s[A-Za-z0-9]){2,15}', fix_handle, text)

    # ── Step 7: Add missing space before $ if preceded by alphanumeric
    text = re.sub(r'([a-zA-Z0-9])(\$[A-Z])', r'\1 \2', text)

    # ── Step 8: Collapse double spaces
    text = re.sub(r' {2,}', ' ', text).strip()

    return text


def repair_text(text: str) -> str:
    """Apply full repair pipeline: exact → regex."""
    if not text:
        return text

    # Pass 1: Exact string fixes
    for bad, good in EXACT_FIXES.items():
        if bad in text:
            text = text.replace(bad, good)

    # Pass 2: Regex fixes
    text = apply_regex_repairs(text)

    # Pass 3: Second pass of exact fixes (after regex may have reordered things)
    for bad, good in EXACT_FIXES.items():
        if bad in text:
            text = text.replace(bad, good)

    return text


def run_repair_v14():
    """Repair all user JSON files by cleaning broken ticker text."""
    print("=" * 60)
    print("V14 FORENSIC REPAIR ENGINE")
    print("Targeting all known ticker fragmentation patterns")
    print("=" * 60)

    files = [f for f in DB_DIR.glob("x_intel_*.json") if f.name != "x_intel_master.json"]

    total_fixed = 0
    log_lines = []

    for file_path in files:
        username = file_path.stem.replace("x_intel_", "")
        print(f"\nProcessing @{username}...")

        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
            posts = raw if isinstance(raw, list) else raw.get("posts", [])

            fixed_count = 0
            for post in posts:
                old_text = post.get("text", "")
                new_text = repair_text(old_text)
                if old_text != new_text:
                    post["text"] = new_text
                    fixed_count += 1
                    log_lines.append(
                        f"[{file_path.name}] ID: {post.get('id', 'N/A')}\n"
                        f"  OLD: {old_text[:150]}\n"
                        f"  NEW: {new_text[:150]}\n"
                    )

            if fixed_count > 0:
                file_path.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"  [OK] Fixed {fixed_count} posts in @{username}")
                total_fixed += fixed_count
            else:
                print(f"  [--] No changes needed for @{username}")

        except Exception as e:
            print(f"  [ERR] Error processing {file_path.name}: {e}")

    # Write repair log
    if log_lines:
        log_path = ROOT / "engine" / "repair_history_v14.txt"
        log_path.write_text("\n".join(log_lines), encoding="utf-8")
        print(f"\n[LOG] Repair log written to engine/repair_history_v14.txt")

    print(f"\n{'=' * 60}")
    print(f"V14 REPAIR COMPLETE: {total_fixed} posts repaired across {len(files)} files")
    print("=" * 60)


if __name__ == "__main__":
    run_repair_v14()
