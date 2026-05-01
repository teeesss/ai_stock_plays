import datetime
import json
import os
from pathlib import Path


class SynopsisArchiveManager:
    """
    V28.8.1: Sovereign Synopsis Archive Manager
    Handles 48-hour rolling history of market intelligence dossiers.
    """

    def __init__(self, root_path=None):
        if root_path:
            self.root = Path(root_path)
        else:
            # Assume we are in engine/ folder
            self.root = Path(__file__).parent.parent

        self.history_path = self.root / "database" / "synopsis_history.json"

    def save_synopsis(self, html_content):
        """
        Saves the full HTML dossier to history with an ISO timestamp.
        Prunes entries older than 48 hours to maintain a high-density, fresh ledger.
        """
        if not html_content or len(html_content) < 100:
            return

        history = self.load_history()

        now = datetime.datetime.now()
        timestamp = now.isoformat()

        # Add new entry
        history[timestamp] = html_content

        # Prune entries older than 48 hours
        cutoff = now - datetime.timedelta(hours=48)
        pruned_history = {}

        # Sort by timestamp to ensure chronological pruning logic
        for ts in sorted(history.keys()):
            try:
                if datetime.datetime.fromisoformat(ts) > cutoff:
                    pruned_history[ts] = history[ts]
            except (ValueError, TypeError):
                continue  # Skip malformed timestamps

        # Ensure directory exists
        os.makedirs(self.history_path.parent, exist_ok=True)

        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(pruned_history, f, indent=2)
            return True
        except Exception as e:
            print(f"[!] Archive Engine Error: Failed to write history: {e}")
            return False

    def load_history(self):
        """Loads the history from the JSON ledger."""
        if not self.history_path.exists():
            return {}
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_latest_archive(self, count=10):
        """Returns the last N archive entries in reverse chronological order."""
        history = self.load_history()
        sorted_keys = sorted(history.keys(), reverse=True)
        return {k: history[k] for k in sorted_keys[:count]}

    def get_history(self):
        """
        Returns the entire 48-hour history as a list of tuples (timestamp, data).
        Sorted reverse-chronologically.
        """
        history = self.load_history()
        # Handle if data is dict-of-dicts (V28.8.1 structure) or just dict-of-strings
        items = []
        for ts in sorted(history.keys(), reverse=True):
            entry = history[ts]
            text = entry.get("text") if isinstance(entry, dict) else entry

            # Format timestamp for humans
            try:
                dt = datetime.datetime.fromisoformat(ts)
                fmt_ts = dt.strftime("%Y-%m-%d %H:%M")
            except:
                fmt_ts = ts

            items.append((fmt_ts, text))

        return items
