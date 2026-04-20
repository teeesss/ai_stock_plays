import json, re
from pathlib import Path

def scan():
    results = ["--- FOREIGN TEXT SCANNER V1.2 ---"]
    files = list(Path("database").glob("x_intel_*.json"))
    for f in files:
        if "master" in f.name: continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            found = 0
            for p in data:
                text = p.get("text", "")
                if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', text):
                    results.append(f"[{f.name}] ID: {p['id']}")
                    results.append(f"  ORIG: {text}")
                    found += 1
            if found > 0:
                results.append(f"Found {found} foreign posts in {f.name}\n")
        except Exception as e:
            results.append(f"Error reading {f.name}: {e}")

    # Write to local file
    Path("engine/foreign_posts.txt").write_text("\n".join(results), encoding="utf-8")
    print(f"SCAN COMPLETE. Results in engine/foreign_posts.txt")

if __name__ == "__main__":
    scan()