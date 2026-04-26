import os
import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# GIGACPO Terminal Menu
# V1.0 - Unified Orchestration
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
ENGINE_DIR = ROOT / "engine"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def run_script(script_name, args=[]):
    script_path = ENGINE_DIR / script_name
    if not script_path.exists():
        print(f"Error: {script_name} not found.")
        input("Press Enter to continue...")
        return

    cmd = [sys.executable, str(script_path)] + args
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Script failed: {e}")
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")

    input("\nDone. Press Enter to return to menu...")


def menu():
    while True:
        clear()
        print("=" * 60)
        print("   GIGACPO FINANCIAL INTELLIGENCE TERMINAL - CONTROL PANEL")
        print("=" * 60)
        print("   [1] DAILY SYNC (Scrape + OCR + Buzz)")
        print("   [2] INSTANT SYNC (Last 24h fast fetch)")
        print("   [3] DEEP SCRAPER (Custom User/Range/Query)")
        print("   [4] MANAGE USERS (Add/Remove monitored handles)")
        print("   [5] LIVE PRICES (Update Pulse data)")
        print("   [6] REBUILD MASTER (Force JSON aggregation)")
        print("   [7] IMAGE ANALYZER (Force OCR pass)")
        print("   [8] TRANSLATE (CJK -> English pass)")
        print("   [9] TICKER REPAIR (Regex forensic clean)")
        print("   [10] INST 13F (Institutional Alpha Fetch)")
        print("   [11] VX RESCUE (Manual Tweet ID Repair)")
        print("-" * 60)
        print("   [U] UPDATE SYSTEM (Vercel Bridge Sync)")
        print("   [Q] QUIT")
        print("=" * 60)

        choice = input("Select Option > ").lower().strip()

        if choice == "1":
            ocr = input("Include OCR (Slow)? (y/n): ").strip().lower()
            if ocr == "n":
                run_script("sync_triple.py", ["--skip-ocr"])
            else:
                run_script("sync_triple.py")
        elif choice == "2":
            run_script("x_intel_instant_sync.py")
        elif choice == "3":
            user = input("Username (optional, leave blank for --all): ").strip().lstrip("@")
            days = input("Max Days (default 210): ").strip()
            args = []
            if user:
                args += ["--username", user]
            else:
                args += ["--all"]
            if days:
                args += ["--days", days]
            run_script("x_intel_deep_scraper.py", args)
        elif choice == "4":
            action = input("Action (add/remove/list): ").strip().lower()
            if action in ["add", "remove"]:
                username = input("Username: ").strip()
                run_script("manage_users.py", [action, username])
            else:
                run_script("manage_users.py", ["list"])
        elif choice == "5":
            run_script("live_prices.py")
        elif choice == "6":
            run_script("rebuild_master.py")
        elif choice == "7":
            run_script("image_analyzer.py")
        elif choice == "8":
            run_script("translate_intel.py")
        elif choice == "9":
            run_script("repair_tickers.py")
        elif choice == "10":
            run_script("inst_13f_fetcher.py")
        elif choice == "11":
            tid = input("Tweet ID to Repair: ").strip()
            if tid:
                run_script("vx_rescue_fetcher.py", [tid])
        elif choice == "u":
            run_script("remote_sync.py")
        elif choice == "q":
            break
        else:
            print("Invalid choice.")
            input("Press Enter...")


if __name__ == "__main__":
    menu()
