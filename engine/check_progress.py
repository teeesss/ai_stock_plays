import json
import os
from datetime import datetime


def check_file(filename):
    path = os.path.join("database", filename)
    if not os.path.exists(path):
        print(f"File {filename} not found.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dates = []
    for item in data:
        if "timestamp" in item:
            try:
                # Handle ISO format or similar
                dt = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                dates.append(dt)
            except:
                pass

    if not dates:
        print(f"{filename}: No valid dates found in {len(data)} items.")
        return

    dates.sort()
    print(f"{filename}: Total: {len(data)}, Earliest: {dates[0]}, Latest: {dates[-1]}")


if __name__ == "__main__":
    files = [
        "x_intel_aleabitoreddit.json",
        "x_intel_PhotonCap.json",
        "x_intel_KawzInvests.json",
    ]
    for f in files:
        check_file(f)
