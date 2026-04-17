import os
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# AI/engine/generate_ui.py
AI_ROOT = Path(__file__).parent.parent
TEMPLATE_PATH = AI_ROOT / "index_template.html"
OUTPUT_PATH = AI_ROOT / "index.html"

def generate():
    if not TEMPLATE_PATH.exists():
        print(f"Error: Template {TEMPLATE_PATH} not found.")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Dynamic Injections can happen here
    # Example: Injected version label or timestamp
    import datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = html.replace("Independent Autonomous Mode", f"Independent Autonomous Mode | Last Generated: {ts}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Generated {OUTPUT_PATH} from template.")

if __name__ == "__main__":
    generate()
