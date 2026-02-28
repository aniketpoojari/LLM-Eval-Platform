import json
import re

from backend.logger.logging import get_logger

logger = get_logger(__name__)


def parse_judge_response(response_text):
    try:
        match = re.search(r'\{[^{}]*"score"\s*:\s*\d+[^{}]*\}', response_text)
        if match:
            result = json.loads(match.group())
            score = int(result.get("score", 0))
            if 1 <= score <= 5:
                return {
                    "score": score,
                    "explanation": result.get("explanation", ""),
                }
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse judge response: {e}")

    score_match = re.search(
        r"(?:score|rating)\s*[:=]\s*(\d)", response_text, re.IGNORECASE
    )
    if score_match:
        score = int(score_match.group(1))
        if 1 <= score <= 5:
            return {"score": score, "explanation": "Extracted from free-text response"}

    logger.warning(f"Could not parse score from: {response_text[:200]}")
    return {
        "score": 3,
        "explanation": "Failed to parse judge response, defaulting to 3",
    }


def compute_aggregate_score(dimension_scores, weights=None):
    if not dimension_scores:
        return 0.0

    if weights is None:
        weights = {d: 1.0 for d in dimension_scores}

    total_weight = sum(weights.get(d, 1.0) for d in dimension_scores)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(
        dimension_scores[d] * weights.get(d, 1.0) for d in dimension_scores
    )
    return round(weighted_sum / total_weight, 2)
