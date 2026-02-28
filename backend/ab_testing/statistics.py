import numpy as np
from scipy import stats

from backend.logger.logging import get_logger

logger = get_logger(__name__)


def paired_t_test(scores_a, scores_b):
    if len(scores_a) != len(scores_b) or len(scores_a) < 2:
        return {"p_value": None, "t_statistic": None, "is_significant": False}

    a = np.array(scores_a, dtype=float)
    b = np.array(scores_b, dtype=float)

    t_stat, p_value = stats.ttest_rel(a, b)

    return {
        "t_statistic": round(float(t_stat), 4),
        "p_value": round(float(p_value), 6),
        "is_significant": p_value < 0.05,
    }


def bootstrap_confidence_interval(
    scores_a, scores_b, n_bootstrap=1000, confidence=0.95
):
    if len(scores_a) < 2 or len(scores_b) < 2:
        return {"lower": None, "upper": None, "mean_diff": None}

    a = np.array(scores_a, dtype=float)
    b = np.array(scores_b, dtype=float)
    diffs = a - b

    rng = np.random.default_rng(42)
    bootstrap_means = []
    for _ in range(n_bootstrap):
        sample = rng.choice(diffs, size=len(diffs), replace=True)
        bootstrap_means.append(np.mean(sample))

    bootstrap_means = np.array(bootstrap_means)
    alpha = 1 - confidence
    lower = float(np.percentile(bootstrap_means, 100 * alpha / 2))
    upper = float(np.percentile(bootstrap_means, 100 * (1 - alpha / 2)))

    return {
        "lower": round(lower, 4),
        "upper": round(upper, 4),
        "mean_diff": round(float(np.mean(diffs)), 4),
    }


def compute_effect_size(scores_a, scores_b):
    a = np.array(scores_a, dtype=float)
    b = np.array(scores_b, dtype=float)

    diff = a - b
    mean_diff = np.mean(diff)
    std_diff = np.std(diff, ddof=1)

    if std_diff == 0:
        return 0.0 if mean_diff == 0 else float("inf")

    cohens_d = mean_diff / std_diff
    return round(float(cohens_d), 4)
