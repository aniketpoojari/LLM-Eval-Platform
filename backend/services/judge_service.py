from langchain_core.messages import HumanMessage, SystemMessage

from backend.evaluation.judge_prompts import (JUDGE_SYSTEM_PROMPT,
                                              get_judge_prompt)
from backend.evaluation.scorers import parse_judge_response
from backend.logger.logging import get_logger
from backend.utils.model_loader import ModelLoader

logger = get_logger(__name__)


class JudgeService:
    def __init__(self):
        self.model_loader = ModelLoader()

    def judge(self, dimension, input_text, actual_output, expected_output=None):
        model = self.model_loader.get_model(temperature=0.0, max_tokens=256)
        prompt = get_judge_prompt(dimension, input_text, actual_output, expected_output)

        try:
            response = model.invoke(
                [
                    SystemMessage(content=JUDGE_SYSTEM_PROMPT),
                    HumanMessage(content=prompt),
                ]
            )

            parsed = parse_judge_response(response.content)
            usage = response.response_metadata.get("token_usage", {})

            return {
                "score": parsed["score"],
                "explanation": parsed["explanation"],
                "token_usage": {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                },
            }
        except Exception as e:
            logger.error(f"Error in judge for {dimension}: {e}")
            return {
                "score": 3,
                "explanation": f"Judge error: {str(e)}",
                "token_usage": {"input_tokens": 0, "output_tokens": 0},
            }

    def judge_multiple(
        self, dimensions, input_text, actual_output, expected_output=None
    ):
        results = {}
        total_usage = {"input_tokens": 0, "output_tokens": 0}

        for dim in dimensions:
            result = self.judge(dim, input_text, actual_output, expected_output)
            results[dim] = {
                "score": result["score"],
                "explanation": result["explanation"],
            }
            total_usage["input_tokens"] += result["token_usage"]["input_tokens"]
            total_usage["output_tokens"] += result["token_usage"]["output_tokens"]

        scores = {d: results[d]["score"] for d in results}
        avg = round(sum(scores.values()) / len(scores), 2) if scores else 0

        return {
            "scores": scores,
            "explanations": {d: results[d]["explanation"] for d in results},
            "avg_score": avg,
            "token_usage": total_usage,
        }
