import asyncio
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


class BatchRunner:
    def __init__(self, db):
        self.db = db
        self.model_loader = ModelLoader()
        self.http_client = AsyncHTTPClient(timeout=30.0)
        self._progress = {}

    async def run_evaluation(self, evaluation_id, target, queries, dimensions):
        self._progress[evaluation_id] = {
            "total": len(queries),
            "completed": 0,
            "status": "running",
        }

        self.db.update(
            "evaluations",
            {"status": "running"},
            "id = ?",
            [evaluation_id],
        )

        results = []
        for i, query in enumerate(queries):
            try:
                result = await self._evaluate_single(
                    evaluation_id, target, query, dimensions
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating query {i}: {e}")
                results.append({"error": str(e)})

            self._progress[evaluation_id]["completed"] = i + 1
            self.db.update(
                "evaluations",
                {"completed_queries": i + 1},
                "id = ?",
                [evaluation_id],
            )

        all_scores = [r.get("avg_score", 0) for r in results if "avg_score" in r]
        avg_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else None

        self.db.update(
            "evaluations",
            {
                "status": "completed",
                "avg_score": avg_score,
                "completed_at": "datetime('now')",
            },
            "id = ?",
            [evaluation_id],
        )

        self._progress[evaluation_id]["status"] = "completed"
        return results

    async def _evaluate_single(self, evaluation_id, target, query, dimensions):
        input_text = query.get("input", "")
        expected_output = query.get("expected_output")

        headers = json.loads(target.get("headers", "{}"))
        template = target.get("request_template", '{"query": "{{input}}"}')
        body_str = template.replace("{{input}}", input_text)
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            body = {"query": input_text}

        response = await self.http_client.send_request(
            method=target.get("api_method", "POST"),
            url=target["api_url"],
            headers=headers,
            json_body=body,
        )

        actual_output = None
        if response.get("json"):
            path_parts = target.get("response_path", "response").split(".")
            data = response["json"]
            for part in path_parts:
                if isinstance(data, dict):
                    data = data.get(part)
                else:
                    data = None
                    break
            actual_output = str(data) if data is not None else str(response["json"])
        else:
            actual_output = response.get("body", "")

        scores = {}
        token_usage = {"input_tokens": 0, "output_tokens": 0}

        model = self.model_loader.get_model(temperature=0.0, max_tokens=256)

        for dimension in dimensions:
            try:
                judge_prompt = get_judge_prompt(
                    dimension, input_text, actual_output, expected_output
                )
                from langchain_core.messages import HumanMessage, SystemMessage

                judge_response = model.invoke(
                    [
                        SystemMessage(content=JUDGE_SYSTEM_PROMPT),
                        HumanMessage(content=judge_prompt),
                    ]
                )

                parsed = parse_judge_response(judge_response.content)
                scores[dimension] = parsed["score"]

                usage = judge_response.response_metadata.get("token_usage", {})
                token_usage["input_tokens"] += usage.get("prompt_tokens", 0)
                token_usage["output_tokens"] += usage.get("completion_tokens", 0)

            except Exception as e:
                logger.error(f"Error judging {dimension}: {e}")
                scores[dimension] = 3

        avg_score = compute_aggregate_score(scores)

        result_id = str(uuid.uuid4())
        self.db.insert(
            "evaluation_results",
            {
                "id": result_id,
                "evaluation_id": evaluation_id,
                "input_text": input_text,
                "expected_output": expected_output,
                "actual_output": actual_output[:5000] if actual_output else None,
                "scores": json.dumps(scores),
                "avg_score": avg_score,
                "latency_ms": response.get("latency_ms"),
                "token_usage": json.dumps(token_usage),
            },
        )

        total_tokens = token_usage["input_tokens"] + token_usage["output_tokens"]
        if total_tokens > 0:
            from backend.config.config_loader import get_config

            config = get_config()
            input_rate = config.get("cost.rates.groq.input_per_1m", 0.05)
            output_rate = config.get("cost.rates.groq.output_per_1m", 0.08)
            cost = (token_usage["input_tokens"] / 1_000_000 * input_rate) + (
                token_usage["output_tokens"] / 1_000_000 * output_rate
            )

            cost_id = str(uuid.uuid4())
            self.db.insert(
                "cost_tracking",
                {
                    "id": cost_id,
                    "source": "evaluation",
                    "source_id": evaluation_id,
                    "provider": "groq",
                    "model": self.model_loader.get_model_info()["model"],
                    "input_tokens": token_usage["input_tokens"],
                    "output_tokens": token_usage["output_tokens"],
                    "total_tokens": total_tokens,
                    "estimated_cost": round(cost, 6),
                },
            )

        return {
            "input": input_text,
            "output": actual_output,
            "scores": scores,
            "avg_score": avg_score,
            "latency_ms": response.get("latency_ms"),
        }

    def get_progress(self, evaluation_id):
        return self._progress.get(evaluation_id, {"status": "unknown"})
