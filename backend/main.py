import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.logger.logging import get_logger, setup_logging
from backend.models.database import DatabaseManager

setup_logging()
logger = get_logger(__name__)

db = None
eval_service = None
red_team_service = None
ab_test_service = None
observability_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, eval_service, red_team_service, ab_test_service, observability_service
    logger.info("Starting LLM Eval Platform...")

    db = DatabaseManager()

    from backend.services.ab_test_service import ABTestService
    from backend.services.evaluation_service import EvaluationService
    from backend.services.observability_service import ObservabilityService
    from backend.services.red_team_service import RedTeamService

    eval_service = EvaluationService(db)
    red_team_service = RedTeamService(db)
    ab_test_service = ABTestService(db)
    observability_service = ObservabilityService(db)

    logger.info("All services initialized")
    yield

    logger.info("Shutting down...")


app = FastAPI(
    title="LLM Eval Platform",
    description="Evaluate, red-team, and A/B test any LLM application",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.routes_ab_test import router as ab_test_router
from backend.api.routes_eval import router as eval_router
from backend.api.routes_health import router as health_router
from backend.api.routes_observability import router as observability_router
from backend.api.routes_red_team import router as red_team_router
from backend.api.routes_targets import router as targets_router

app.include_router(health_router)
app.include_router(targets_router)
app.include_router(eval_router)
app.include_router(red_team_router)
app.include_router(ab_test_router)
app.include_router(observability_router)

# Serve static frontend in production
frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "frontend", "dist"
)
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
