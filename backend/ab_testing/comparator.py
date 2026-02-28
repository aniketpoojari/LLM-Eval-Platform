import json

from backend.ab_testing.statistics import (bootstrap_confidence_interval,
                                           compute_effect_size, paired_t_test)
from backend.logger.logging import get_logger

logger = get_logger(__name__)


class ABComparator:
    def __init__(self, db):
        self.db = db

    def compare(self, experiment_id):
        results = self.db.fetch_all(
            "SELECT * FROM ab_results WHERE experiment_id = ? ORDER BY created_at",
            [experiment_id],
        )

        if not results:
            return None

        scores_a = [r["avg_score_a"] for r in results if r["avg_score_a"] is not None]
        scores_b = [r["avg_score_b"] for r in results if r["avg_score_b"] is not None]

        if not scores_a or not scores_b:
            return None

        t_test = paired_t_test(scores_a, scores_b)
        ci = bootstrap_confidence_interval(scores_a, scores_b)
        effect = compute_effect_size(scores_a, scores_b)

        dim_scores_a = {}
        dim_scores_b = {}
        for r in results:
            sa = json.loads(r.get("scores_a", "{}"))
            sb = json.loads(r.get("scores_b", "{}"))
            for dim, score in sa.items():
                dim_scores_a.setdefault(dim, []).append(score)
            for dim, score in sb.items():
                dim_scores_b.setdefault(dim, []).append(score)

        per_dim_a = {d: round(sum(s) / len(s), 2) for d, s in dim_scores_a.items() if s}
        per_dim_b = {d: round(sum(s) / len(s), 2) for d, s in dim_scores_b.items() if s}

        avg_a = round(sum(scores_a) / len(scores_a), 2)
        avg_b = round(sum(scores_b) / len(scores_b), 2)

        winner = None
        if t_test["is_significant"]:
            winner = "A" if avg_a > avg_b else "B"

        return {
            "total_queries": len(results),
            "scores_a": per_dim_a,
            "scores_b": per_dim_b,
            "avg_a": avg_a,
            "avg_b": avg_b,
            "winner": winner,
            "p_value": t_test["p_value"],
            "confidence_interval": ci,
            "effect_size": effect,
            "is_significant": t_test["is_significant"],
        }
