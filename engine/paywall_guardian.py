import json
import logging
import os
import re
import time
import zipfile
from pathlib import Path

from curl_cffi import requests

# V29.5: Paywall Guardian Engine
log = logging.getLogger(__name__)


class PaywallGuardian:
    """
    V29.5: Institutional Paywall Guardian.
    Automates the monitoring and synchronization of the 'Bypass Paywalls' ruleset.
    Ensures the engine stays ahead of institutional gatekeepers.
    """

    SOURCE_URL = "https://gitflic.ru/project/magnolia1234/bypass-paywalls-chrome-clean"
    ZIP_URL = "https://gitflic.ru/project/magnolia1234/bypass-paywalls-chrome-clean/file/downloadAll?format=zip&branch=master"
    STATE_FILE = "database/paywall_state.json"
    TARGET_DIR = "FreePaywall"

    @classmethod
    def check_for_updates(cls, force=False):
        """
        Main entry point. Checks if 24 hours have passed since the last update check.
        If force=True, ignores the timestamp.
        """
        root = Path(__file__).parent.parent
        state_path = root / cls.STATE_FILE

        state = {"last_check": 0, "last_version": "unknown", "last_commit": "unknown"}
        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except:
                pass

        now = time.time()
        # 24h = 86400 seconds
        if not force and (now - state.get("last_check", 0)) < 86400:
            return False

        print("[INFO] [GUARDIAN] Checking for Paywall Intelligence updates...")

        try:
            # 1. Fetch the project page to find the latest commit hash
            resp = requests.get(cls.SOURCE_URL, impersonate="chrome110", timeout=15)
            if resp.status_code != 200:
                print(f"[WARN] [GUARDIAN] Failed to reach GitFlic: {resp.status_code}")
                return False

            # Extract the commit hash from the HTML (look for commit link)
            # Example: /commit/a4f9a042a41c347c99a2655d30c3b740bfcefc3b
            match = re.search(r"\/commit\/([a-f0-9]{40})", resp.text)
            latest_commit = match.group(1) if match else "unknown"

            if (
                latest_commit == state.get("last_commit")
                and latest_commit != "unknown"
                and not force
            ):
                print(
                    f"[INFO] [GUARDIAN] Paywall Intelligence is up to date (Commit: {latest_commit[:8]})."
                )
                state["last_check"] = now
                cls._save_state(state_path, state)
                return False

            print(
                f"[INFO] [GUARDIAN] New version detected! [{latest_commit[:8]}]. Triggering intelligence refresh..."
            )

            # 2. Download the Zip
            zip_path = root / "scratch" / "paywall_update.zip"
            zip_path.parent.mkdir(parents=True, exist_ok=True)

            z_resp = requests.get(cls.ZIP_URL, impersonate="chrome110", timeout=30)
            if z_resp.status_code != 200:
                print(f"[ERROR] [GUARDIAN] Failed to download zip: {z_resp.status_code}")
                return False

            with open(zip_path, "wb") as f:
                f.write(z_resp.content)

            # 3. Unzip and Sync
            extract_dir = root / "scratch" / "paywall_extracted"
            if extract_dir.exists():
                import shutil

                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # The zip often has a nested folder named 'bypass-paywalls-chrome-clean-master'
            # V29.5: Hardened source detection to prevent "Not a directory" errors if ZIP has multiple root items
            items = list(extract_dir.iterdir())
            if len(items) == 1 and items[0].is_dir():
                source_folder = items[0]
            else:
                source_folder = extract_dir

            target_dir = root / cls.TARGET_DIR
            target_dir.mkdir(parents=True, exist_ok=True)

            # Copy all files from source to target
            import shutil

            for item in source_folder.iterdir():
                dest = target_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

            print(
                f"[SUCCESS] [GUARDIAN] Paywall Intelligence synced to V29.5 standards (Commit: {latest_commit[:8]})."
            )

            # 4. Update State
            state["last_check"] = now
            state["last_commit"] = latest_commit
            cls._save_state(state_path, state)

            # Clean up
            if zip_path.exists():
                os.remove(zip_path)
            shutil.rmtree(extract_dir)

            return True

        except Exception as e:
            print(f"[ERROR] [GUARDIAN] Intelligence sync failed: {e}")
            return False

    @staticmethod
    def _save_state(path, state):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except:
            pass


if __name__ == "__main__":
    # Test run
    PaywallGuardian.check_for_updates(force=True)
