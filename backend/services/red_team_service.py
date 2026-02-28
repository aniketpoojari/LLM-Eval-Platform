import asyncio
import json
import uuid

from backend.logger.logging import get_logger
from backend.models.pydantic_models import RedTeamRunCreate, RedTeamRunResponse
from backend.red_team.attack_library import (get_attack_count_by_category,
                                             sample_attacks)
from backend.red_team.categories import get_all_categories
from backend.red_team.safety_scorer import SafetyScorer
from backend.utils.http_client import AsyncHTTPClient

logger = get_logger(__name__)


class RedTeamService:
    def __init__(self, db):
        self.db = db
        self.safety_scorer = SafetyScorer()
        self.http_client = AsyncHTTPClient(timeout=30.0)
        self._progress = {}

    async def create_run(self, request: RedTeamRunCreate):
        run_id = str(uuid.uuid4())
        categories = [c.value for c in request.categories]

        max_per_cat = None
        if request.max_attacks:
            max_per_cat = max(1, request.max_attacks // len(categories))

        attacks = sample_attacks(categories, max_per_cat)
        total = len(attacks)

        self.db.insert(
            "red_team_runs",
            {
                "id": run_id,
                "name": request.name,
                "target_id": request.target_id,
                "categories": json.dumps(categories),
                "status": "pending",
                "total_attacks": total,
                "completed_attacks": 0,
            },
        )

        target = self.db.fetch_one(
            "SELECT * FROM targets WHERE id = ?", [request.target_id]
        )
        if not target:
            self.db.update("red_team_runs", {"status": "failed"}, "id = ?", [run_id])
            raise ValueError(f"Target {request.target_id} not found")

        asyncio.create_task(self._run_attacks(run_id, target, attacks))

        row = self.db.fetch_one("SELECT * FROM red_team_runs WHERE id = ?", [run_id])
        return RedTeamRunResponse.from_db(row)

    async def _run_attacks(self, run_id, target, attacks):
        self._progress[run_id] = {
            "total": len(attacks),
            "completed": 0,
            "status": "running",
            "safe": 0,
            "unsafe": 0,
        }

        self.db.update("red_team_runs", {"status": "running"}, "id = ?", [run_id])

        safe_count = 0
        total_score = 0.0

        for i, attack in enumerate(attacks):
            try:
                result = await self._execute_attack(run_id, target, attack)
                if result["is_safe"]:
                    safe_count += 1
                    self._progress[run_id]["safe"] += 1
                else:
                    self._progress[run_id]["unsafe"] += 1
                total_score += result.get("safety_score", 0)
            except Exception as e:
                logger.error(f"Attack error: {e}")
                safe_count += 1

            self._progress[run_id]["completed"] = i + 1
            self.db.update(
                "red_team_runs",
                {"completed_attacks": i + 1},
                "id = ?",
                [run_id],
            )

        safety_score = round(total_score / len(attacks), 3) if attacks else 1.0

        self.db.update(
            "red_team_runs",
            {
                "status": "completed",
                "safety_score": safety_score,
                "completed_at": "datetime('now')",
            },
            "id = ?",
            [run_id],
        )

        self._progress[run_id]["status"] = "completed"

    async def _execute_attack(self, run_id, target, attack):
        headers = json.loads(target.get("headers", "{}"))
        template = target.get("request_template", '{"query": "{{input}}"}')
        body_str = template.replace("{{input}}", attack["input"])

        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            body = {"query": attack["input"]}

        response = await self.http_client.send_request(
            method=target.get("api_method", "POST"),
            url=target["api_url"],
            headers=headers,
            json_body=body,
        )

        output = None
        if response.get("json"):
            path_parts = target.get("response_path", "response").split(".")
            data = response["json"]
            for part in path_parts:
                if isinstance(data, dict):
                    data = data.get(part)
                else:
                    data = None
                    break
            output = str(data) if data is not None else str(response["json"])
        else:
            output = response.get("body", "")

        safety = self.safety_scorer.score(
            attack["category"],
            attack["input"],
            output,
        )

        result_id = str(uuid.uuid4())
        self.db.insert(
            "red_team_results",
            {
                "id": result_id,
                "run_id": run_id,
                "category": attack["category"],
                "subcategory": attack.get("subcategory"),
                "attack_name": attack["name"],
                "attack_input": attack["input"],
                "target_output": output[:5000] if output else None,
                "is_safe": 1 if safety["is_safe"] else 0,
                "safety_score": safety["safety_score"],
                "explanation": safety["explanation"],
                "latency_ms": response.get("latency_ms"),
            },
        )

        return safety

    async def stream_progress(self, run_id):
        while True:
            progress = self._progress.get(run_id, {"status": "unknown"})
            if progress.get("status") == "unknown":
                row = self.db.fetch_one(
                    "SELECT * FROM red_team_runs WHERE id = ?", [run_id]
                )
                if row:
                    progress = {
                        "total": row["total_attacks"],
                        "completed": row["completed_attacks"],
                        "status": row["status"],
                    }

            yield f"data: {json.dumps(progress)}\n\n"

            if progress.get("status") in ("completed", "failed"):
                break
            await asyncio.sleep(1)

    def get_attack_library(self, category=None):
        from backend.red_team.attack_library import get_attacks_by_category

        attacks = get_attacks_by_category(category)
        return [
            {
                "name": a["name"],
                "category": a["category"],
                "subcategory": a.get("subcategory"),
                "input_preview": (
                    a["input"][:100] + "..." if len(a["input"]) > 100 else a["input"]
                ),
            }
            for a in attacks
        ]

    def get_categories(self):
        categories = get_all_categories()
        counts = get_attack_count_by_category()
        for cat in categories:
            cat["attack_count"] = counts.get(cat["id"], 0)
        return categories
