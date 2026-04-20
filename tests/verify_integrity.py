import os
import sys
import re
import py_compile
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENGINE_DIR = ROOT / "engine"

def test_engine_syntax():
    """Verify all engine scripts are syntactically valid."""
    print("Checking engine script syntax...")
    python_files = list(ENGINE_DIR.glob("*.py")) + list((ENGINE_DIR / "scraper").glob("*.py"))
    
    errors = []
    for f in python_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        # Check for forbidden patterns
        if ".resolve()" in content:
            print(f"VIOLATION: {f.name} - Contains .resolve()! Use .absolute() or relative paths to preserve drive letters.")
            errors.append(str(f))

        try:
            py_compile.compile(str(f), doraise=True)
            # print(f"PASS: {f.name}")
        except py_compile.PyCompileError as e:
            print(f"FAIL: {f.name} - {e}")
            errors.append(str(f))
    
    if errors:
        print(f"\nFound {len(errors)} syntax errors!")
        sys.exit(1)
    print("All engine scripts passed syntax check.")

def test_emoji_fluff():
    """Ensure no emojis in log/print calls (avoid Windows encoding issues)."""
    print("Scanning for emoji fluff in engine logs...")
    emoji_pattern = re.compile(r'[^\x00-\x7F]')
    
    files = list(ENGINE_DIR.glob("*.py")) + [ROOT / "terminal.py"]
    
    violations = []
    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.splitlines(), 1):
            if any(x in line for x in ["log.", "print(", "print ("]):
                if emoji_pattern.search(line):
                    clean_line = emoji_pattern.sub("[?]", line).strip()
                    print(f"VIOLATION: {f.name}:{line_num} - Found non-ASCII: {clean_line}")
                    violations.append(f"{f.name}:{line_num}")

    if violations:
        print(f"\nFound {len(violations)} emoji/UTF-8 violations in terminal output logic!")
        # sys.exit(1) # Warning only for now? No, make it fail to enforce.
        sys.exit(1)
    print("No emoji fluff detected in logs.")

if __name__ == "__main__":
    test_engine_syntax()
    test_emoji_fluff()
    print("\nINTEGRITY CHECK COMPLETE")
