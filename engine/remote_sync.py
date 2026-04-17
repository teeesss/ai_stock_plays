"""
engine/remote_sync.py
=====================
Handles secure SFTP deployment of the CPO Dashboard to the remote web server.
Uses credentials from credentials/vault.json.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import paramiko

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("remote_sync")

ROOT = Path(__file__).parent.parent

def get_creds():
    host = os.environ.get("SFTP_HOST")
    user = os.environ.get("SFTP_USER")
    pas  = os.environ.get("SFTP_PASS")
    path = os.environ.get("SFTP_PATH")
    
    if not all([host, user, pas, path]):
        log.error("Missing SFTP credentials in .env")
        return None
        
    return {
        "remote": {
            "host": host,
            "user": user,
            "pass": pas,
            "path": path
        }
    }

def sync(from_dist=False):
    creds = get_creds()
    if not creds or "remote" not in creds:
        log.error("Missing remote credentials.")
        return False

    remote = creds["remote"]
    
    if from_dist:
        base_dir = ROOT / "dist"
        if not base_dir.exists():
            log.error("dist directory not found. Run build first.")
            return False
        # In dist mode, we sync EVERYTHING in dist
        files_to_sync = {}
        for p in base_dir.rglob("*"):
            if p.is_file():
                rel = p.relative_to(base_dir)
                files_to_sync[str(rel)] = str(rel).replace("\\", "/")
    else:
        base_dir = ROOT
        # Mapping local paths to remote paths
        files_to_sync = {
            "cpo_plays.html": "index.html",
            "database/dashboard_data.js": "database/dashboard_data.js",
            "database/live_prices.js": "database/live_prices.js",
            "database/intel.js": "intel.js"
        }

    transport = None
    try:
        log.info(f"Connecting to {remote['host']} (SFTP)...")
        transport = paramiko.Transport((remote["host"], 22))
        transport.connect(username=remote["user"], password=remote["pass"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Navigate using relative parts
        target_parts = remote["path"].strip("/").split("/")
        for part in target_parts:
            try:
                sftp.chdir(part)
                log.info(f"Changed to {part}")
            except FileNotFoundError:
                log.info(f"Creating directory {part}")
                sftp.mkdir(part)
                sftp.chmod(part, 0o755)
                sftp.chdir(part)

        # Ensure database subdir exists
        try:
            sftp.stat("database")
        except FileNotFoundError:
            log.info("Creating database directory")
            sftp.mkdir("database")
            sftp.chmod("database", 0o755)

        for local_rel, remote_rel in files_to_sync.items():
            local_path = base_dir / local_rel
            if not local_path.exists():
                log.warning(f"Skipping missing file: {local_path}")
                continue

            # For database/ files, we need to ensure the remote rel is correct
            # Since we are already in the 'stocks' dir, database/dashboard_data.js is correct
            log.info(f"Uploading {local_rel} -> {remote_rel}...")
            sftp.put(str(local_path), remote_rel)
            sftp.chmod(remote_rel, 0o644)

        sftp.close()
        transport.close()
        log.info("Secure SFTP sync completed successfully.")
        return True

    except Exception as e:
        log.error(f"Secure Sync Failed: {e}")
        if transport: transport.close()
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", action="store_true", help="Sync from dist folder")
    args = parser.parse_args()
    sync(from_dist=args.dist)
