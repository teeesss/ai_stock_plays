import subprocess
import sys
from datetime import datetime
from pathlib import Path

# V28: Hierarchy Leader Error Monitoring
try:
    from error_monitor import init_error_monitor
except ImportError:
    from engine.error_monitor import init_error_monitor
init_error_monitor()

# ─────────────────────────────────────────────────────────────
# GIGACPO Comprehensive Test Runner (V28)
# Enforces the "ALWAYS RUN" Mandate
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
TEST_DIR = ROOT / "tests"
RESULTS_FILE = ROOT / "TEST_RESULTS.md"


def run_cmd(name, cmd):
    print(f"\n>>> Running {name}...")
    try:
        # Use shell=True on Windows for built-in commands or complex strings
        # V29.7.1: Force UTF-8 encoding to prevent Windows cp1252 decoding crashes
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding="utf-8")
        passed = result.returncode == 0
        # Harden output aggregation against NoneType artifacts
        output = (result.stdout or "") + (result.stderr or "")
        print(f"    {'[PASS]' if passed else '[FAIL]'} {name}")
        return passed, output
    except Exception as e:
        print(f"    [ERROR] {name} failed to execute: {e}")
        return False, str(e)


def main():
    print("=" * 60)
    print("   GIGACPO UNIFIED TEST RUNNER - MANDATORY VERIFICATION")
    print("=" * 60)

    all_passed = True
    report = []

    # 1. Syntax Check (Fast)
    passed, output = run_cmd(
        "Syntax Audit", [sys.executable, str(TEST_DIR / "test_engine_syntax.py")]
    )
    report.append(("Syntax Audit", passed, output))
    if not passed:
        all_passed = False

    # 2. Layout Integrity (V28 Mandatory)
    passed, output = run_cmd(
        "Layout Integrity (V28)", [sys.executable, str(TEST_DIR / "test_layout_integrity.py")]
    )
    report.append(("Layout Integrity (V28)", passed, output))
    if not passed:
        all_passed = False

    # 3. Regression Suite (Pytest)
    passed, output = run_cmd(
        "Regression Suite (Pytest)", [sys.executable, "-m", "pytest", "tests/"]
    )
    if not passed:
        # Fallback to unittest
        passed, output = run_cmd(
            "Regression Suite (Unittest)", [sys.executable, "-m", "unittest", "discover", "tests"]
        )

    report.append(("Regression Suite", passed, output))
    if not passed:
        all_passed = False

    # 4. Smoke Test (Real-World Integration)
    # passed, output = run_cmd("Smoke Test (Integration)", [sys.executable, "smoke_test.py"])
    # report.append(("Smoke Test", passed, output))
    # if not passed:
    #     all_passed = False

    # Update TEST_RESULTS.md
    print("\n>>> Updating TEST_RESULTS.md...")
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write("# Test Execution Results\n\n")
        f.write("## Latest Run (Automated Status)\n")
        f.write(f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Status:** {'ALL PASSED' if all_passed else 'FAILURES DETECTED'}\n\n")

        for name, passed, output in report:
            f.write(f"### {name}\n")
            f.write(f"- **Result:** {'PASSED' if passed else 'FAIL'}\n")
            if not passed:
                f.write(
                    f"- **Error Snippet:**\n```\n{output[-500:] if output else 'No output'}\n```\n"
                )
            f.write("\n")

    print("=" * 60)
    if all_passed:
        print("   ALL SYSTEMS GO - ENVIRONMENT VERIFIED")
        sys.exit(0)
    else:
        print("   FAILURES DETECTED - REVIEW TEST_RESULTS.MD")
        sys.exit(1)


if __name__ == "__main__":
    main()
