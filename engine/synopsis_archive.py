import datetime
import json
import os
from pathlib import Path


class SynopsisArchiveManager:
    """
    V28.8.2: Sovereign Synopsis Archive Manager
    Handles 48-hour rolling history of market intelligence dossiers.
    Saves dossiers as individual HTML files for direct URL access.
    """

    def __init__(self, root_path=None):
        if root_path:
            self.root = Path(root_path)
        else:
            self.root = Path(__file__).parent.parent

        self.history_path = self.root / "database" / "synopsis_history.json"
        self.dossiers_dir = self.root / "web" / "archive" / "dossiers"

    def save_synopsis(self, html_content):
        """
        Saves the full HTML dossier as a standalone file.
        Updates the JSON ledger with metadata and prunes old files/entries.
        """
        if not html_content or len(html_content) < 100:
            return

        os.makedirs(self.dossiers_dir, exist_ok=True)
        os.makedirs(self.history_path.parent, exist_ok=True)

        now = datetime.datetime.now()
        timestamp = now.isoformat()
        safe_ts = now.strftime("%Y-%m-%d_%H%M")
        filename = f"synopsis_{safe_ts}.html"
        file_path = self.dossiers_dir / filename

        # 1. Save the actual HTML file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        except Exception as e:
            print(f"[!] Archive Engine Error: Failed to save dossier file: {e}")
            return False

        # 2. Update JSON history
        history = self.load_history()
        history[timestamp] = {"filename": filename}

        # 3. Prune entries/files older than 48 hours
        cutoff = now - datetime.timedelta(hours=48)
        pruned_history = {}

        # Keep track of active filenames to avoid deleting what we just saved or what is still valid
        active_files = set()

        for ts in sorted(history.keys()):
            try:
                dt = datetime.datetime.fromisoformat(ts)
                entry = history[ts]
                entry_filename = entry.get("filename") if isinstance(entry, dict) else None

                if dt > cutoff:
                    pruned_history[ts] = entry
                    if entry_filename:
                        active_files.add(entry_filename)
                else:
                    # Entry is old, delete file if it exists
                    if entry_filename:
                        old_file = self.dossiers_dir / entry_filename
                        if old_file.exists():
                            try:
                                os.remove(old_file)
                            except:
                                pass
            except (ValueError, TypeError):
                continue

        # Clean up any stray files in dossiers_dir that aren't in active_files
        try:
            for f in os.listdir(self.dossiers_dir):
                if f.startswith("synopsis_") and f.endswith(".html") and f not in active_files:
                    try:
                        os.remove(self.dossiers_dir / f)
                    except:
                        pass
        except:
            pass

        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(pruned_history, f, indent=2)
            return str(file_path)  # Return path for sync
        except Exception as e:
            print(f"[!] Archive Engine Error: Failed to write history: {e}")
            return None

    def load_history(self):
        """Loads the history from the JSON ledger."""
        if not self.history_path.exists():
            return {}
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Migration: if data contains strings instead of dicts, it's the old format
                # We'll just return it and save_synopsis will handle/overwrite it
                return data
        except Exception:
            return {}

    def get_history(self):
        """
        Returns history as list of tuples (fmt_ts, filename).
        Sorted reverse-chronologically.
        """
        history = self.load_history()
        items = []
        for ts in sorted(history.keys(), reverse=True):
            entry = history[ts]
            # Handle migration or dict format
            if isinstance(entry, dict):
                filename = entry.get("filename")
            else:
                # Old format had the full HTML content as a string
                # We can't easily retrieve a filename, so skip
                continue

            if not filename:
                continue

            try:
                dt = datetime.datetime.fromisoformat(ts)
                fmt_ts = dt.strftime("%Y-%m-%d %H:%M")
            except:
                fmt_ts = ts

            items.append((fmt_ts, filename))

        return items
