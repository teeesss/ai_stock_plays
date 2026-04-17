import json
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "database"
USER_FILE = DB_DIR / "monitored_users.json"

def load_users():
    if USER_FILE.exists():
        return json.loads(USER_FILE.read_text(encoding="utf-8"))
    return []

def save_users(users):
    USER_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")

def add_user(username):
    users = load_users()
    username = username.strip().lstrip("@")
    if username not in users:
        users.append(username)
        save_users(users)
        print(f"Added @{username}")
    else:
        print(f"@{username} already exists")

def remove_user(username):
    users = load_users()
    username = username.strip().lstrip("@")
    if username in users:
        users.remove(username)
        save_users(users)
        print(f"Removed @{username}")
    else:
        print(f"@{username} not found")

def list_users():
    users = load_users()
    print("Monitored Users:")
    for u in users:
        print(f"- @{u}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage monitored X usernames")
    parser.add_argument("action", choices=["add", "remove", "list"])
    parser.add_argument("username", nargs="?", help="X username to add/remove")
    
    args = parser.parse_args()
    
    if args.action == "add":
        if not args.username:
            print("Error: username required for add")
        else:
            add_user(args.username)
    elif args.action == "remove":
        if not args.username:
            print("Error: username required for remove")
        else:
            remove_user(args.username)
    elif args.action == "list":
        list_users()
