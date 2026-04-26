"""
server.py
=========
GIGACPO Web Server Bridge
=========================
Serves the CPO Intelligence Terminal and automates
post-market data syncs via APScheduler.

FEATURES:
  - Full web server: hosts cpo_plays.html at http://localhost:5174
  - /api/sync      : manually triggers the full data pipeline
  - /api/prices    : triggers live price fetch only
  - /api/status    : returns last-sync timestamp + entry count
  - Scheduler      : auto-runs at 4:20 PM EST (21:20 UTC) Mon-Fri
                     (20 minutes after US market close; all global
                      exchanges use this single sync window)

INSTALL DEPS (one-time):
  pip install fastapi uvicorn apscheduler

RUN:
  python server.py
  Then open: http://localhost:5174
"""

from __future__ import annotations

import json
import logging
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

# ── Dependencies ─────────────────────────────────────────────────────────────
try:
    from engine.dependency_mgr import ensure_dependencies

    ensure_dependencies()
except ImportError:
    pass


# ── FastAPI / APScheduler (Protected by ensure_dependencies) ──────────────────
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ── Setup ─────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("gigacpo")

ROOT = Path(__file__).parent
DB_PATH = ROOT / "database" / "CPO_MASTER_DATA.json"

app = FastAPI(title="GIGACPO Terminal", version="6.1")

# ── Static File Serving ───────────────────────────────────────────────────────
# Mount the database folder so JS can fetch dashboard_data.js + live_prices.js
app.mount("/database", StaticFiles(directory=str(ROOT / "database")), name="database")
# Mount images if they exist
images_dir = ROOT / "images"
if images_dir.exists():
    app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")


@app.get("/")
async def serve_terminal():
    """Serve the main CPO Intelligence Terminal."""
    return FileResponse(str(ROOT / "cpo_plays.html"))


# ── Sync State ────────────────────────────────────────────────────────────────
_sync_lock = threading.Lock()
_sync_state = {
    "running": False,
    "last_sync": None,
    "last_result": None,
}


def _get_entry_count() -> int:
    try:
        with open(DB_PATH, encoding="utf-8") as f:
            d = json.load(f)
        return len(d)
    except Exception:
        return 0


def _run_pipeline(pipeline: str = "full") -> dict:
    """
    Execute the data pipeline in a subprocess.
    pipeline options: 'full', 'prices'
    """
    if not _sync_lock.acquire(blocking=False):
        return {
            "status": "busy",
            "message": "A sync is already running. Try again shortly.",
        }

    _sync_state["running"] = True
    result = {"status": "ok", "pipeline": pipeline, "steps": []}

    try:
        steps = {
            "full": [
                ["python", "engine/financial_auditor.py"],
                ["python", "engine/live_prices.py"],
                ["python", "engine/generate_CPO_BRAIN.py"],
                ["python", "engine/remote_sync.py"],
            ],
            "prices": [
                ["python", "engine/live_prices.py"],
                ["python", "engine/remote_sync.py"],
            ],
        }.get(pipeline, [])

        for cmd in steps:
            step_name = " ".join(cmd[1:])
            log.info(f"  Running: {step_name}")
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(ROOT),
                    timeout=600,
                )
                step_result = {
                    "cmd": step_name,
                    "returncode": proc.returncode,
                    "ok": proc.returncode == 0,
                }
                if proc.returncode != 0:
                    step_result["stderr"] = proc.stderr[-500:] if proc.stderr else ""
                result["steps"].append(step_result)
                log.info(f"  {'OK' if proc.returncode == 0 else 'FAILED'}: {step_name}")
            except subprocess.TimeoutExpired:
                result["steps"].append({"cmd": step_name, "ok": False, "error": "timeout"})
                log.warning(f"  TIMEOUT: {step_name}")

        _sync_state["last_sync"] = datetime.now(timezone.utc).isoformat()
        _sync_state["last_result"] = result

    except Exception as ex:
        result["status"] = "error"
        result["error"] = str(ex)
        log.error(f"Pipeline error: {ex}")

    finally:
        _sync_state["running"] = False
        _sync_lock.release()

    return result


# ── API Endpoints ─────────────────────────────────────────────────────────────
@app.get("/api/status")
async def api_status():
    """Return current sync status and database summary."""
    return JSONResponse(
        {
            "status": "running" if _sync_state["running"] else "idle",
            "last_sync": _sync_state["last_sync"],
            "entry_count": _get_entry_count(),
            "server_time": datetime.now(timezone.utc).isoformat(),
            "schedule": "4:20 PM EST (21:20 UTC) Mon-Fri",
        }
    )


@app.post("/api/sync")
async def api_sync_full():
    """Trigger a full pipeline sync (financial_auditor + live_prices + brain)."""
    if _sync_state["running"]:
        return JSONResponse(
            {"status": "busy", "message": "Sync already in progress."}, status_code=409
        )
    # Run in background thread so HTTP responds quickly
    t = threading.Thread(target=_run_pipeline, args=("full",), daemon=True)
    t.start()
    return JSONResponse(
        {
            "status": "started",
            "message": "Full sync initiated. Check /api/status for progress.",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
    )


@app.post("/api/prices")
async def api_sync_prices():
    """Trigger a live-prices-only sync (fast, ~30 seconds)."""
    if _sync_state["running"]:
        return JSONResponse(
            {"status": "busy", "message": "Sync already in progress."}, status_code=409
        )
    t = threading.Thread(target=_run_pipeline, args=("prices",), daemon=True)
    t.start()
    return JSONResponse(
        {
            "status": "started",
            "message": "Live price refresh initiated.",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
    )


# ── Scheduler ─────────────────────────────────────────────────────────────────
def scheduled_sync():
    """Called automatically at 4:20 PM EST (21:20 UTC) Mon-Fri."""
    log.info("=== SCHEDULED SYNC: 4:20 PM EST market-close trigger ===")
    result = _run_pipeline("full")
    ok_count = sum(1 for s in result.get("steps", []) if s.get("ok"))
    total = len(result.get("steps", []))
    log.info(f"=== SCHEDULED SYNC COMPLETE: {ok_count}/{total} steps OK ===")


scheduler = BackgroundScheduler(timezone="UTC")
scheduler.add_job(
    scheduled_sync,
    trigger=CronTrigger(
        day_of_week="mon-fri",
        hour=21,
        minute=20,
        timezone="UTC",
    ),
    id="market_close_sync",
    name="Post-Market Close Full Sync (4:20 PM EST)",
    replace_existing=True,
)


# ── Startup / Shutdown ────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    scheduler.start()
    entries = _get_entry_count()
    log.info(f"GIGACPO Terminal v6.0 starting — {entries} ecosystem entries loaded")
    log.info("Scheduler active: full sync at 4:20 PM EST (21:20 UTC) Mon-Fri")
    log.info("Dashboard: http://localhost:5174")


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown(wait=False)
    log.info("Server stopped.")


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=5174,
        reload=False,
        log_level="info",
    )
