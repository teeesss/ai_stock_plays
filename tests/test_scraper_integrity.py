import json
import re
from pathlib import Path

ROOT = Path("z:/COS_Stock_Plays")
DB_DIR = ROOT / "database"

def test_database_integrity():
    files = [f for f in DB_DIR.glob("x_intel_*.json") if f.name != "x_intel_master.json"]
    if not files:
        print("No database files found to test.")
        return

    all_passed = True

    for file_path in files:
        print(f"\nTesting {file_path.name}...")
        try:
            content = file_path.read_text(encoding="utf-8")
            data = json.loads(content)
        except Exception as e:
            print(f"[FAIL] Failed to parse JSON: {e}")
            all_passed = False
            continue

        if not isinstance(data, list):
            print("[FAIL] Root JSON structure is not a list")
            all_passed = False
            continue

        seen_ids = set()
        duplicates = 0
        missing_fields = 0
        spacing_errors = 0

        for post in data:
            # 1. Required fields
            if not all(k in post for k in ["id", "text", "timestamp"]):
                missing_fields += 1
                
            post_id = post.get("id")
            if post_id:
                if post_id in seen_ids:
                    duplicates += 1
                seen_ids.add(post_id)

            text = post.get("text", "")
            # 2. Check spacing around $ticker
            if re.search(r'\$[a-zA-Z]{1,10}[A-Za-z0-9]', text):
                # E.g. $AAOItoday is bad. We expect no alphanumeric connected directly to the end of a ticker constraint in typical cases.
                # Actually, our scraper cleaner does: r'(\$[a-z]{2,10})([a-zA-Z0-9])' -> but we have to be careful not to trigger on $100K.
                # Just checking if there's $ followed by letters then another letter without space.
                # It's easier to run the exact regex from the scraper and see if any matches exist.
                pass
                
            if re.search(r'\$[a-zA-Z]{2,10}(?=[a-zA-Z0-9])', text, re.IGNORECASE):
                # Wait, our scraper replaces $TICKER followed by alphanumeric. Let's just check if it was caught.
                pass
                
        # Better spacing check based strictly on scraper's regex:
        for post in data:
            text = post.get("text", "")
            if re.search(r'(\$[a-zA-Z]{2,10})(?=[a-zA-Z0-9])', text): # If a $TICKER is immediately followed by more alphanumeric (it shouldn't be if clean_text_spacing worked, wait, $AAOI followed by 'today' -> $AAOI today. Yes).
                # Actually, $AAOI is [a-zA-Z]. If the regex was `(\$[a-z]{2,10})([a-zA-Z0-9])`, it only replaced lowercase.
                pass
                
        # I will strictly use the inverse of the cleaned state to find errors:
        for post in data:
            text = post.get("text", "")
            # Check $ticker (lowercase or uppercase) followed by alphanumeric? 
            # In deep_scraper it was: r'(\$[a-z]{2,10})([a-zA-Z0-9])'. 
            # If we find that exact pattern, it means the cleaner missed it or wasn't run.
            if re.search(r'\$[a-z]{2,10}[a-zA-Z0-9]', text):
                spacing_errors += 1
            if re.search(r'@[A-Za-z0-9_]{1,20}[a-zA-Z0-9]', text):
                # Wait, @USER is allowed to have alphanumeric. The boundary is hard to test cleanly without false positives here since @user2 exists.
                # The scraper replaces `(@[A-Za-z0-9_]{1,20})([a-zA-Z0-9])`, wait, the original regex was flawed if it replaced @user2 -> @user 2.
                pass

        print(f"  Total posts: {len(data)}")
        print(f"  Unique posts: {len(seen_ids)}")
        
        if duplicates > 0:
            print(f"  [FAIL] FOUND {duplicates} DUPLICATES")
            all_passed = False
        else:
            print("  [OK] No duplicates")
            
        if missing_fields > 0:
            print(f"  [FAIL] FOUND {missing_fields} posts missing required fields")
            all_passed = False
        else:
            print("  [OK] All required fields present")
            
        if spacing_errors > 0:
            print(f"  [WARN] FOUND {spacing_errors} possible spacing errors (historical data might need reprocessing)")
            # we won't fail the overall test for historical data, but we flag it.

    if all_passed:
        print("\n[OK] All databases passed integrity checks.")
        import sys
        sys.exit(0)
    else:
        print("\n[FAIL] Integrity checks failed. Please review logs.")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    test_database_integrity()
