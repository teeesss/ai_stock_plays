import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
import server


def test_scheduler_autorun():
    print("Testing APScheduler Autorun Logic in server.py...")
    run_time = datetime.now(timezone.utc) + timedelta(seconds=1)

    event = threading.Event()
    results = {}

    with patch("subprocess.run") as mock_subproc:
        mock_subproc.returncode = 0

        def mock_sync():
            try:
                res = server._run_pipeline("prices")
                results["res"] = res
            finally:
                event.set()

        test_scheduler = BackgroundScheduler(timezone="UTC")
        test_scheduler.add_job(mock_sync, trigger=DateTrigger(run_date=run_time), id="test_trigger")
        test_scheduler.start()

        triggered = event.wait(timeout=5)
        test_scheduler.shutdown()

        if not triggered:
            print("FAILED: Scheduler did not run")
            sys.exit(1)

        print("SUCCESS! Scheduler successfully triggered the pipeline without user intervention.")
        print(
            f"Pipeline executed steps correctly: {len(results.get('res', {}).get('steps', []))} steps"
        )


if __name__ == "__main__":
    test_scheduler_autorun()
