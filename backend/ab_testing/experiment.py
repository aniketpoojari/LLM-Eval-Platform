import json
import uuid

from backend.evaluation.judge_prompts import (JUDGE_SYSTEM_PROMPT,
                                              get_judge_prompt)
from backend.evaluation.scorers import (compute_aggregate_score,
                                        parse_judge_response)
from backend.logger.logging import get_logger
from backend.utils.http_client import AsyncHTTPClient
from backend.utils.model_loader import ModelLoader

logger = get_logger(__name__)


class ExperimentRunner:
    def __init__(self, db):
        self.db = db
        self.model_loader = ModelLoader()
        self.http_client = AsyncHTTPClient(timeout=30.0)
        self._progress = {}

    async def run_experiment(
        self, experiment_id, target_a, target_b, queries, dimensions
    ):
        self._progress[experiment_id] = {
            "total": len(queries),
            "completed": 0,
            "status": "running",
        }

        self.db.update(
            "ab_experiments", {"status": "running"}, "id = ?", [experiment_id]
        )

        all_scores_a = []
        all_scores_b = []

        for i, query in enumerate(queries):
            try:
                result = await self._run_pair(
                    experiment_id, target_a, target_b, query, dimensions
                )
                if result.get("avg_score_a") is not None:
                    all_scores_a.append(result["avg_score_a"])
                if result.get("avg_score_b") is not None:
                    all_scores_b.append(result["avg_score_b"])
            except Exception as e:
                logger.error(f"Pair error for query {i}: {e}")

            self._progress[experiment_id]["completed"] = i + 1
            self.db.update(
                "ab_experiments",
                {"completed_queries": i + 1},
                "id = ?",
                [experiment_id],
            )

        winner = None
        if all_scores_a and all_scores_b:
            avg_a = sum(all_scores_a) / len(all_scores_a)
            avg_b = sum(all_scores_b) / len(all_scores_b)

            from backend.ab_testing.statistics import paired_t_test

            test_result = paired_t_test(all_scores_a, all_scores_b)

            if test_result["is_significant"]:
                winner = "A" if avg_a > avg_b else "B"

            self.db.update(
                "ab_experiments",
                {
                    "status": "completed",
                    "winner": winner,
                    "statistical_significance": test_result.get("p_value"),
                    "completed_at": "datetime('now')",
                },
                "id = ?",
                [experiment_id],
            )
        else:
            self.db.update(
                "ab_experiments",
                {"status": "completed", "completed_at": "datetime('now')"},
                "id = ?",
                [experiment_id],
            )

        self._progress[experiment_id]["status"] = "completed"

    async def _run_pair(self, experiment_id, target_a, target_b, query, dimensions):
        response_a = await self._send_to_target(target_a, query)
        response_b = await self._send_to_target(target_b, query)

        model = self.model_loader.get_model(temperature=0.0, max_tokens=256)
        scores_a = {}
        scores_b = {}

        for dim in dimensions:
            for label, output, scores_dict in [
                ("A", response_a["output"], scores_a),
                ("B", response_b["output"], scores_b),
            ]:
                try:
                    prompt = get_judge_prompt(dim, query, output)
                    from langchain_core.messages import (HumanMessage,
                                                         SystemMessage)

                    resp = model.invoke(
                        [
                            SystemMessage(content=JUDGE_SYSTEM_PROMPT),
                            HumanMessage(content=prompt),
                        ]
                    )
                    parsed = parse_judge_response(resp.content)
                    scores_dict[dim] = parsed["score"]
                except Exception as e:
                    logger.error(f"Judge error {label}/{dim}: {e}")
                    scores_dict[dim] = 3

        avg_a = compute_aggregate_score(scores_a)
        avg_b = compute_aggregate_score(scores_b)

        result_id = str(uuid.uuid4())
        self.db.insert(
            "ab_results",
            {
                "id": result_id,
                "experiment_id": experiment_id,
                "input_text": query,
                "output_a": (response_a["output"] or "")[:5000],
                "output_b": (response_b["output"] or "")[:5000],
                "scores_a": json.dumps(scores_a),
                "scores_b": json.dumps(scores_b),
                "avg_score_a": avg_a,
                "avg_score_b": avg_b,
                "latency_a_ms": response_a.get("latency_ms"),
                "latency_b_ms": response_b.get("latency_ms"),
            },
        )

        return {"avg_score_a": avg_a, "avg_score_b": avg_b}

    async def _send_to_target(self, target, query):
        headers = json.loads(target.get("headers", "{}"))
        template = target.get("request_template", '{"query": "{{input}}"}')
        body_str = template.replace("{{input}}", query)

        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            body = {"query": query}

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

        return {
            "output": output,
            "latency_ms": response.get("latency_ms", 0),
        }

    def get_progress(self, experiment_id):
        return self._progress.get(experiment_id, {"status": "unknown"})
