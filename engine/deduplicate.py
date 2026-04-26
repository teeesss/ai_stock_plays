import json
from pathlib import Path


def deduplicate():
    print("V12.0 DATA HYGIENE - DEDUPLICATION")
    db_path = Path("database")
    files = list(db_path.glob("x_intel_*.json"))

    for f in files:
        if "master" in f.name:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            seen = set()
            clean_data = []
            dupes = 0
            for item in data:
                # Use ID as primary key
                pid = str(item.get("id"))
                if pid not in seen:
                    seen.add(pid)
                    clean_data.append(item)
                else:
                    dupes += 1

            if dupes > 0:
                f.write_text(
                    json.dumps(clean_data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                print(f"  Removed {dupes} duplicates from {f.name}")
            else:
                print(f"  No duplicates in {f.name}")
        except Exception as e:
            print(f"  Error processing {f.name}: {e}")


if __name__ == "__main__":
    deduplicate()
