import hmac
import os
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query, Response

from services.pipeline import run_pipeline

router = APIRouter()

# In-memory store for the last background run result.
# Sufficient for a single-process deployment (Railway runs one dyno).
_last_run: dict = {}


def _run_and_store() -> None:
    global _last_run
    try:
        result = run_pipeline(dry_run=False)
        _last_run = {"status": "success", **result}
    except Exception as e:
        _last_run = {"status": "error", "error": str(e)}


def _check_auth(authorization: str | None) -> None:
    secret = os.environ.get("SCRAPE_SECRET")
    if not secret:
        return
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Constant-time comparison prevents timing-based secret enumeration
    if not hmac.compare_digest(authorization, f"Bearer {secret}"):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/scrape")
def scrape(
    response: Response,
    background_tasks: BackgroundTasks,
    dry_run: bool = Query(False),
    authorization: str = Header(None),
):
    _check_auth(authorization)

    if dry_run:
        # Synchronous — useful for testing; returns full topic payload.
        # Note: still makes full AI API calls; not cheap.
        return run_pipeline(dry_run=True)

    # Prevent concurrent scrapes — a retry from the cron caller would
    # otherwise race with the in-progress run and duplicate today's data.
    if _last_run.get("status") == "running":
        response.status_code = 409
        return {
            "status": "already_running",
            "message": "A scrape is already in progress. Check GET /scrape/status.",
            "started_at": _last_run.get("started_at"),
        }

    _last_run["status"] = "running"
    _last_run["started_at"] = datetime.now(timezone.utc).isoformat()
    background_tasks.add_task(_run_and_store)
    response.status_code = 202
    return {
        "status": "queued",
        "message": "Scrape started. Poll GET /scrape/status for the result.",
    }


@router.get("/scrape/status")
def scrape_status(authorization: str = Header(None)):
    _check_auth(authorization)
    if not _last_run:
        return {"status": "never_run"}
    return _last_run
