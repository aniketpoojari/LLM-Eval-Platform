import asyncio
import json
import uuid

from backend.ab_testing.comparator import ABComparator
from backend.ab_testing.experiment import ExperimentRunner
from backend.logger.logging import get_logger
from backend.models.pydantic_models import (ABExperimentResponse, ABTestCreate,
                                            ABTestStats)

logger = get_logger(__name__)


class ABTestService:
    def __init__(self, db):
        self.db = db
        self.runner = ExperimentRunner(db)
        self.comparator = ABComparator(db)

    async def create_experiment(self, request: ABTestCreate):
        exp_id = str(uuid.uuid4())
        dimensions = [d.value for d in request.dimensions]

        self.db.insert(
            "ab_experiments",
            {
                "id": exp_id,
                "name": request.name,
                "target_a_id": request.target_a_id,
                "target_b_id": request.target_b_id,
                "dimensions": json.dumps(dimensions),
                "status": "pending",
                "total_queries": len(request.queries),
                "completed_queries": 0,
            },
        )

        target_a = self.db.fetch_one(
            "SELECT * FROM targets WHERE id = ?", [request.target_a_id]
        )
        target_b = self.db.fetch_one(
            "SELECT * FROM targets WHERE id = ?", [request.target_b_id]
        )

        if not target_a or not target_b:
            self.db.update("ab_experiments", {"status": "failed"}, "id = ?", [exp_id])
            raise ValueError("One or both targets not found")

        asyncio.create_task(
            self.runner.run_experiment(
                exp_id, target_a, target_b, request.queries, dimensions
            )
        )

        row = self.db.fetch_one("SELECT * FROM ab_experiments WHERE id = ?", [exp_id])
        return ABExperimentResponse.from_db(row)

    async def get_statistics(self, experiment_id):
        experiment = self.db.fetch_one(
            "SELECT * FROM ab_experiments WHERE id = ?", [experiment_id]
        )
        if not experiment:
            return None

        comparison = self.comparator.compare(experiment_id)
        if not comparison:
            return None

        target_a = self.db.fetch_one(
            "SELECT name FROM targets WHERE id = ?", [experiment["target_a_id"]]
        )
        target_b = self.db.fetch_one(
            "SELECT name FROM targets WHERE id = ?", [experiment["target_b_id"]]
        )

        return ABTestStats(
            experiment_id=experiment_id,
            target_a_name=target_a["name"] if target_a else "Unknown",
            target_b_name=target_b["name"] if target_b else "Unknown",
            total_queries=comparison["total_queries"],
            scores_a=comparison["scores_a"],
            scores_b=comparison["scores_b"],
            avg_a=comparison["avg_a"],
            avg_b=comparison["avg_b"],
            winner=comparison["winner"],
            p_value=comparison["p_value"],
            confidence_interval=comparison["confidence_interval"],
            is_significant=comparison["is_significant"],
        )

    async def stream_progress(self, experiment_id):
        while True:
            progress = self.runner.get_progress(experiment_id)
            if progress.get("status") == "unknown":
                row = self.db.fetch_one(
                    "SELECT * FROM ab_experiments WHERE id = ?", [experiment_id]
                )
                if row:
                    progress = {
                        "total": row["total_queries"],
                        "completed": row["completed_queries"],
                        "status": row["status"],
                    }

            yield f"data: {json.dumps(progress)}\n\n"

            if progress.get("status") in ("completed", "failed"):
                break
            await asyncio.sleep(1)
