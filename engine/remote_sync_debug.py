"""
engine/remote_sync_debug.py
===========================
Debug pathing for SFTP.
"""
import paramiko
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
VAULT_PATH = ROOT / "credentials" / "vault.json"

with open(VAULT_PATH, "r") as f:
    creds = json.load(f)["remote"]

transport = paramiko.Transport((creds["host"], 22))
transport.connect(username=creds["user"], password=creds["pass"])
sftp = paramiko.SFTPClient.from_transport(transport)

print(f"Current SFTP Dir: {sftp.getcwd()}")
print("Listing contents:")
for f in sftp.listdir():
    print(f" - {f}")

sftp.close()
transport.close()
