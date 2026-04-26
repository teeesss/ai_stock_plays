import subprocess
import sys
import time
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# GIGACPO Real-World Smoke Test (RWST)
# V1.0 — Forensic Verification Layer
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
ENGINE_DIR = ROOT / "engine"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def run_step(name, script_path, args=[]):
    print(f"\n[RWST] STEP: {name}")
    print(f"      Target: {script_path}")

    cmd = [sys.executable, str(script_path)] + args
    try:
        # Run with timeout to prevent hanging in "Real World"
        # Increased to 1200s for large batches (13F / Scraper)
        subprocess.run(cmd, check=True, timeout=1200)
        print(f"      [PASS] {name}")
        return True
    except Exception as e:
        print(f"      [FAIL] {name} | Error: {e}")
        return False


def smoke_test():
    print("=" * 60)
    print("   GIGACPO REAL-WORLD SMOKE TEST — PIPELINE VERIFICATION")
    print("=" * 60)

    steps = [
        ("Institutional Alpha (13F)", ENGINE_DIR / "inst_13f_fetcher.py", []),
        ("Ticker Forensic Repair", ENGINE_DIR / "repair_tickers.py", []),
        ("Master Rebuild (JS Bridge)", ENGINE_DIR / "rebuild_master.py", []),
        ("Live Prices (HTTP Probe)", ENGINE_DIR / "live_prices.py", []),
        (
            "Scraper Modular Kernel (Integration Check)",
            ENGINE_DIR / "x_intel_deep_scraper.py",
            ["--username", "PhotonCap", "--days", "1"],
        ),
        ("Image Analysis (OCR Engine)", ENGINE_DIR / "image_analyzer.py", []),
        ("Visual Buzz Aggregation", ENGINE_DIR / "visual_buzz_aggregator.py", []),
    ]

    results = []
    for name, path, args in steps:
        if not path.exists():
            print(f"      ⚠️ SKIP: {name} (Script missing: {path.name})")
            continue
        results.append(run_step(name, path, args))
        time.sleep(1)  # Breath between sub-processes

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"   SUMMARY: {passed}/{total} Steps Succeeded")
    print("=" * 60)

    if passed == total:
        print("   🚀 PIPELINE IS FLIGHT-READY (V16.2)")
    else:
        print("   ⚠️ PIPELINE HAS DEGRADED — AUDIT LOGS IMMEDIATELY")
        sys.exit(1)


if __name__ == "__main__":
    smoke_test()
