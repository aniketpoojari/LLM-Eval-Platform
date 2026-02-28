import asyncio
import json
import uuid

from backend.evaluation.batch_runner import BatchRunner
from backend.logger.logging import get_logger
from backend.models.pydantic_models import EvaluationCreate, EvaluationResponse

logger = get_logger(__name__)


class EvaluationService:
    def __init__(self, db):
        self.db = db
        self.batch_runner = BatchRunner(db)

    async def create_evaluation(self, request: EvaluationCreate):
        eval_id = str(uuid.uuid4())
        dimensions = [d.value for d in request.dimensions]

        self.db.insert(
            "evaluations",
            {
                "id": eval_id,
                "name": request.name,
                "target_id": request.target_id,
                "dimensions": json.dumps(dimensions),
                "status": "pending",
                "total_queries": len(request.queries),
                "completed_queries": 0,
            },
        )

        target = self.db.fetch_one(
            "SELECT * FROM targets WHERE id = ?", [request.target_id]
        )
        if not target:
            self.db.update(
                "evaluations",
                {"status": "failed"},
                "id = ?",
                [eval_id],
            )
            raise ValueError(f"Target {request.target_id} not found")

        asyncio.create_task(
            self.batch_runner.run_evaluation(
                eval_id, target, [q.model_dump() for q in request.queries], dimensions
            )
        )

        row = self.db.fetch_one("SELECT * FROM evaluations WHERE id = ?", [eval_id])
        return EvaluationResponse.from_db(row)

    async def stream_progress(self, evaluation_id):
        while True:
            progress = self.batch_runner.get_progress(evaluation_id)
            if progress.get("status") == "unknown":
                row = self.db.fetch_one(
                    "SELECT * FROM evaluations WHERE id = ?", [evaluation_id]
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

    def get_evaluation(self, evaluation_id):
        return self.db.fetch_one(
            "SELECT * FROM evaluations WHERE id = ?", [evaluation_id]
        )
