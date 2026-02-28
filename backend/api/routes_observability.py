from fastapi import APIRouter

from backend.models.pydantic_models import CostSummary, MetricSummary

router = APIRouter(prefix="/api/observability", tags=["Observability"])


def get_db():
    from backend.main import db

    return db


def get_obs_service():
    from backend.main import observability_service

    return observability_service


@router.get("/summary", response_model=MetricSummary)
async def get_summary():
    svc = get_obs_service()
    return svc.get_summary()


@router.get("/tokens")
async def get_token_usage(days: int = 30):
    svc = get_obs_service()
    return svc.get_token_timeseries(days)


@router.get("/costs", response_model=CostSummary)
async def get_costs(days: int = 30):
    svc = get_obs_service()
    return svc.get_cost_summary(days)


@router.get("/latency")
async def get_latency(days: int = 30):
    svc = get_obs_service()
    return svc.get_latency_timeseries(days)


@router.get("/scores")
async def get_score_trends(days: int = 30):
    svc = get_obs_service()
    return svc.get_score_trends(days)
