from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models.pydantic_models import (ABExperimentResponse,
                                            ABResultResponse, ABTestCreate,
                                            ABTestStats)

router = APIRouter(prefix="/api/ab-tests", tags=["A/B Testing"])


def get_db():
    from backend.main import db

    return db


def get_ab_service():
    from backend.main import ab_test_service

    return ab_test_service


@router.post("", response_model=ABExperimentResponse)
async def create_ab_test(request: ABTestCreate):
    svc = get_ab_service()
    experiment = await svc.create_experiment(request)
    return experiment


@router.get("", response_model=list[ABExperimentResponse])
async def list_ab_tests():
    db = get_db()
    rows = db.fetch_all("SELECT * FROM ab_experiments ORDER BY created_at DESC")
    return [ABExperimentResponse.from_db(r) for r in rows]


@router.get("/{experiment_id}", response_model=ABExperimentResponse)
async def get_ab_test(experiment_id: str):
    db = get_db()
    row = db.fetch_one("SELECT * FROM ab_experiments WHERE id = ?", [experiment_id])
    if not row:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return ABExperimentResponse.from_db(row)


@router.get("/{experiment_id}/results", response_model=list[ABResultResponse])
async def get_ab_results(experiment_id: str):
    db = get_db()
    rows = db.fetch_all(
        "SELECT * FROM ab_results WHERE experiment_id = ? ORDER BY created_at",
        [experiment_id],
    )
    return [ABResultResponse.from_db(r) for r in rows]


@router.get("/{experiment_id}/stats", response_model=ABTestStats)
async def get_ab_stats(experiment_id: str):
    svc = get_ab_service()
    stats = await svc.get_statistics(experiment_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return stats


@router.get("/{experiment_id}/progress")
async def ab_test_progress(experiment_id: str):
    svc = get_ab_service()
    return StreamingResponse(
        svc.stream_progress(experiment_id),
        media_type="text/event-stream",
    )
