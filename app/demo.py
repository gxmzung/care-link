"""Presentation dashboard routes backed by reproducible synthetic experiments."""

from functools import lru_cache
from pathlib import Path
from threading import Lock

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from .benchmark import run
from .scenario_benchmark import evaluate


router = APIRouter(prefix="/demo", tags=["demo"])
_dashboard_path = Path(__file__).with_name("static") / "dashboard.html"
_scenario_lock = Lock()


@lru_cache(maxsize=1)
def _scenario_results():
    """Run the expensive benchmark once per process until explicitly refreshed."""
    return evaluate(seeds=range(10), count=8, time_limit_seconds=1)


def _get_scenario_results(*, refresh: bool = False):
    # FastAPI executes these sync routes in a thread pool. The lock prevents two
    # first-load/refresh requests from running the same ten optimizations at once.
    with _scenario_lock:
        if refresh:
            _scenario_results.cache_clear()
        return _scenario_results()


@router.get("/result")
def result():
    try:
        return run()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/scenarios")
def scenarios():
    try:
        return _get_scenario_results()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/scenarios/refresh")
def refresh_scenarios():
    """Clear the process cache and return a newly calculated benchmark."""
    try:
        return _get_scenario_results(refresh=True)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("", response_class=HTMLResponse)
def page():
    return _dashboard_path.read_text(encoding="utf-8")
