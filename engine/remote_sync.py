"""
engine/remote_sync.py
=====================
Handles secure SFTP deployment of the CPO Dashboard to the remote web server.
Uses credentials from credentials/vault.json.
"""

import os
import json
import paramiko
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("remote_sync")

ROOT = Path(__file__).parent.parent
VAULT_PATH = ROOT / "credentials" / "vault.json"

def get_creds():
    if not VAULT_PATH.exists():
        log.error(f"Vault not found at {VAULT_PATH}")
        return None
    try:
        with open(VAULT_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Error reading vault: {e}")
        return None

def sync():
    creds = get_creds()
    if not creds or "remote" not in creds:
        log.error("Missing remote credentials.")
        return False

    remote = creds["remote"]
    # Mapping local paths to remote paths
    files_to_sync = {
        "cpo_plays.html": "index.html",
        "database/dashboard_data.js": "database/dashboard_data.js",
        "database/live_prices.js": "database/live_prices.js"
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
                sftp.chdir(part)

        # Ensure database subdir exists
        try:
            sftp.stat("database")
        except FileNotFoundError:
            log.info("Creating database directory")
            sftp.mkdir("database")

        for local_rel, remote_rel in files_to_sync.items():
            local_path = ROOT / local_rel
            if not local_path.exists():
                log.warning(f"Skipping missing file: {local_path}")
                continue

            # For database/ files, we need to ensure the remote rel is correct
            # Since we are already in the 'stocks' dir, database/dashboard_data.js is correct
            log.info(f"Uploading {local_rel} -> {remote_rel}...")
            sftp.put(str(local_path), remote_rel)

        sftp.close()
        transport.close()
        log.info("Secure SFTP sync completed successfully.")
        return True

    except Exception as e:
        log.error(f"Secure Sync Failed: {e}")
        if transport: transport.close()
        return False

if __name__ == "__main__":
    sync()
