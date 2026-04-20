import json
from pathlib import Path

def repair_json(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"File {file_path} not found.")
        return

    print(f"Attempting to repair {file_path}...")
    try:
        content = path.read_text(encoding="utf-8")
        # Try to find the last valid JSON array end
        # Sometimes it's truncated or has extra junk
        
        # Method 1: Try to load as is
        try:
            json.loads(content)
            print("JSON is already valid.")
            return
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            
            # Method 2: Truncate at error point and close array
            # This is a brute force approach for truncated logs
            error_char_pos = e.pos
            truncated = content[:error_char_pos]
            
            # Find last valid list item end
            last_bracket = truncated.rfind('}')
            if last_bracket != -1:
                fixed = truncated[:last_bracket+1] + "\n]"
                try:
                    json.loads(fixed)
                    path.write_text(fixed, encoding="utf-8")
                    print(f"Repaired by truncating at char {last_bracket}. Saved.")
                    return
                except:
                    pass
            
            print("Failed to repair automatically.")
    except Exception as e:
        print(f"Repair process error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        repair_json(sys.argv[1])
    else:
        # Check all intel files
        DB_DIR = Path("database")
        for f in DB_DIR.glob("x_intel_*.json"):
            repair_json(f)