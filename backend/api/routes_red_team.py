from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models.pydantic_models import (RedTeamResultResponse,
                                            RedTeamRunCreate,
                                            RedTeamRunResponse)

router = APIRouter(prefix="/api/red-team", tags=["Red Team"])


def get_db():
    from backend.main import db

    return db


def get_red_team_service():
    from backend.main import red_team_service

    return red_team_service


@router.post("/runs", response_model=RedTeamRunResponse)
async def create_red_team_run(request: RedTeamRunCreate):
    svc = get_red_team_service()
    run = await svc.create_run(request)
    return run


@router.get("/runs", response_model=list[RedTeamRunResponse])
async def list_red_team_runs():
    db = get_db()
    rows = db.fetch_all("SELECT * FROM red_team_runs ORDER BY created_at DESC")
    return [RedTeamRunResponse.from_db(r) for r in rows]


@router.get("/runs/{run_id}", response_model=RedTeamRunResponse)
async def get_red_team_run(run_id: str):
    db = get_db()
    row = db.fetch_one("SELECT * FROM red_team_runs WHERE id = ?", [run_id])
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    return RedTeamRunResponse.from_db(row)


@router.get("/runs/{run_id}/results", response_model=list[RedTeamResultResponse])
async def get_red_team_results(run_id: str):
    db = get_db()
    rows = db.fetch_all(
        "SELECT * FROM red_team_results WHERE run_id = ? ORDER BY created_at",
        [run_id],
    )
    return [RedTeamResultResponse.from_db(r) for r in rows]


@router.get("/runs/{run_id}/progress")
async def red_team_progress(run_id: str):
    svc = get_red_team_service()
    return StreamingResponse(
        svc.stream_progress(run_id),
        media_type="text/event-stream",
    )


@router.get("/attacks")
async def list_attacks(category: str = None):
    svc = get_red_team_service()
    attacks = svc.get_attack_library(category)
    return attacks


@router.get("/categories")
async def list_categories():
    svc = get_red_team_service()
    return svc.get_categories()
