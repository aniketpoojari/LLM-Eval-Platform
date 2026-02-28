import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.ab_testing.statistics import (bootstrap_confidence_interval,
                                           compute_effect_size, paired_t_test)


class TestPairedTTest:
    def test_identical_scores(self):
        scores = [3.0, 4.0, 3.5, 4.5, 3.0]
        result = paired_t_test(scores, scores)
        assert result["p_value"] is not None
        assert not result["is_significant"]

    def test_different_scores(self):
        scores_a = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
        scores_b = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        result = paired_t_test(scores_a, scores_b)
        assert result["is_significant"]
        assert result["p_value"] < 0.05

    def test_insufficient_data(self):
        result = paired_t_test([3.0], [4.0])
        assert not result["is_significant"]
        assert result["p_value"] is None

    def test_mismatched_lengths(self):
        result = paired_t_test([3.0, 4.0], [5.0])
        assert not result["is_significant"]


class TestBootstrapCI:
    def test_basic_ci(self):
        scores_a = [4.0, 4.5, 3.5, 4.0, 5.0]
        scores_b = [3.0, 3.5, 3.0, 2.5, 4.0]
        result = bootstrap_confidence_interval(scores_a, scores_b)
        assert result["lower"] is not None
        assert result["upper"] is not None
        assert result["mean_diff"] is not None
        assert result["lower"] <= result["mean_diff"] <= result["upper"]

    def test_insufficient_data(self):
        result = bootstrap_confidence_interval([3.0], [4.0])
        assert result["lower"] is None

    def test_identical_scores_ci_around_zero(self):
        scores = [3.0, 4.0, 3.5, 4.5, 3.0]
        result = bootstrap_confidence_interval(scores, scores)
        assert result["mean_diff"] == 0.0


class TestEffectSize:
    def test_zero_effect(self):
        scores = [3.0, 4.0, 3.5]
        result = compute_effect_size(scores, scores)
        assert result == 0.0

    def test_large_effect(self):
        a = [5.0, 5.0, 5.0, 5.0, 5.0]
        b = [1.0, 1.0, 1.0, 1.0, 1.0]
        result = compute_effect_size(a, b)
        assert abs(result) > 1.0  # large effect
