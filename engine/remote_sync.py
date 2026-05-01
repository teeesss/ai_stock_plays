"""
engine/remote_sync.py
=====================
Handles secure SFTP deployment of the CPO Dashboard to the remote web server.
Uses credentials from credentials/vault.json.
"""

import logging
import os
from pathlib import Path

import paramiko
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("remote_sync")

ROOT = Path(__file__).parent.parent


class RemoteSync:
    @staticmethod
    def get_creds():
        host = os.environ.get("SFTP_HOST")
        user = os.environ.get("SFTP_USER")
        pas = os.environ.get("SFTP_PASS")
        path = os.environ.get("SFTP_PATH")

        if not all([host, user, pas, path]):
            log.error("Missing SFTP credentials in .env")
            return None

        return {"remote": {"host": host, "user": user, "pass": pas, "path": path}}

    @staticmethod
    def sync_files(files_to_sync, base_dir=ROOT):
        """Syncs a specific dictionary of {local_rel_path: remote_rel_path} to SFTP."""
        creds = RemoteSync.get_creds()
        if not creds:
            return False
        remote = creds["remote"]

        transport = None
        try:
            log.info(f"Connecting to {remote['host']} (SFTP)...")
            transport = paramiko.Transport((remote["host"], 22))
            transport.connect(username=remote["user"], password=remote["pass"])
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Navigate to root target
            target_parts = remote["path"].strip("/").split("/")
            for part in target_parts:
                try:
                    sftp.chdir(part)
                except FileNotFoundError:
                    sftp.mkdir(part)
                    sftp.chdir(part)

            for local_rel, remote_rel in files_to_sync.items():
                local_path = base_dir / local_rel
                if not local_path.exists():
                    log.warning(f"Skipping missing file: {local_path}")
                    continue

                remote_parent = os.path.dirname(remote_rel)
                if remote_parent:
                    parts = remote_parent.split("/")
                    curr_rem = ""
                    for part in parts:
                        if not part:
                            continue
                        curr_rem = f"{curr_rem}/{part}" if curr_rem else part
                        try:
                            sftp.stat(curr_rem)
                        except FileNotFoundError:
                            sftp.mkdir(curr_rem)

                # V23.60: Delta Sync Optimization (Skip if size matches)
                local_size = local_path.stat().st_size
                try:
                    remote_stat = sftp.stat(remote_rel)
                    if remote_stat.st_size == local_size:
                        log.info(f"Skipping {local_rel} (Size match: {local_size}b)")
                        continue
                except FileNotFoundError:
                    pass  # Upload as new

                log.info(f"Uploading {local_rel} -> {remote_rel} ({local_size}b)...")
                sftp.put(str(local_path), remote_rel)
                sftp.chmod(remote_rel, 0o644)

            sftp.close()
            transport.close()
            log.info("Secure SFTP sync completed successfully.")
            return True
        except Exception as e:
            log.error(f"Secure Sync Failed: {e}")
            if transport:
                transport.close()
            return False

    @staticmethod
    def sync_file(abs_path):
        """Convenience method to sync a single file. Bypasses mount mismatches by string anchoring."""
        try:
            abs_str = str(abs_path).replace("\\", "/")

            # Find the persistent folder name as anchor
            anchor = "COS_Stock_Plays/"
            if anchor in abs_str:
                rel_path = abs_str.split(anchor)[-1]
            else:
                rel_path = os.path.basename(abs_path)

            # Force lowercase for remote consistency (Linux servers)
            rel_path = rel_path.replace("\\", "/")  # Ensure forward slashes
            rem_path = rel_path

            if rem_path.lower().startswith("web/semi/"):
                rem_path = rem_path[9:]  # Strip 'web/semi/'
                if rem_path == "dashboard_data.js":
                    rem_path = "database/dashboard_data.js"
            elif rem_path.lower().startswith("web/ai/"):
                rem_path = rem_path[7:]  # Strip 'web/ai/'
                if rem_path == "dashboard_data.js":
                    rem_path = "database/dashboard_data.js"
                rem_path = "ai/" + rem_path

            elif rem_path.lower().startswith("web/archive/"):
                rem_path = rem_path[12:]  # Strip 'web/archive/'
                rem_path = "archive/" + rem_path

            if rem_path.lower() == "cpo_plays.html":
                rem_path = "index.html"
            elif rem_path.lower() == "database/synopsis_preview.html":
                rem_path = "email/index.html"

            log.info(f"Targeting relative path for sync: {rel_path}")
            return RemoteSync.sync_files({rel_path: rem_path}, base_dir=ROOT)
        except Exception as e:
            log.error(f"Sync file failed: {e}")
            return False

    @staticmethod
    def sync(from_dist=False):
        if from_dist:
            base_dir = ROOT / "dist"
            if not base_dir.exists():
                return False
            files_to_sync = {
                str(p.relative_to(base_dir)): str(p.relative_to(base_dir)).replace("\\", "/")
                for p in base_dir.rglob("*")
                if p.is_file()
            }
            return RemoteSync.sync_files(files_to_sync, base_dir=base_dir)
        else:
            files_to_sync = {}

            # 1. Semi Mapping (bmwseals.com/stocks)
            semi_local = ROOT / "web" / "semi"
            if semi_local.exists():
                files_to_sync["web/semi/index.html"] = "index.html"
                files_to_sync["web/semi/dashboard_data.js"] = "database/dashboard_data.js"

            # 2. AI Mapping (bmwseals.com/stocks/ai)
            ai_local = ROOT / "web" / "ai"
            if ai_local.exists():
                files_to_sync["web/ai/index.html"] = "ai/index.html"
                files_to_sync["web/ai/dashboard_data.js"] = "ai/database/dashboard_data.js"

            # 3. Archive Mapping (bmwseals.com/stocks/archive)
            arch_local = ROOT / "web" / "archive"
            if arch_local.exists():
                # V28.8.2: Sync all files in archive recursively (including dossiers)
                for p in arch_local.rglob("*"):
                    if p.is_file():
                        rel_path = str(p.relative_to(ROOT)).replace("\\", "/")
                        rem_path = str(p.relative_to(arch_local)).replace("\\", "/")
                        rem_path = "archive/" + rem_path
                        files_to_sync[rel_path] = rem_path

            # 4. Global prices
            files_to_sync["database/live_prices.js"] = "database/live_prices.js"

            # 5. Email Synopsis (bmwseals.com/email)
            files_to_sync["database/synopsis_preview.html"] = "email/index.html"

            return RemoteSync.sync_files(files_to_sync, base_dir=ROOT)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", action="store_true", help="Sync from dist folder")
    args = parser.parse_args()
    RemoteSync.sync(from_dist=args.dist)
