import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.evaluation.dimensions import (get_all_dimensions,
                                           get_dimension_info)
from backend.evaluation.judge_prompts import get_judge_prompt
from backend.evaluation.scorers import (compute_aggregate_score,
                                        parse_judge_response)


class TestScorers:
    def test_parse_valid_json(self):
        response = '{"score": 4, "explanation": "Good response"}'
        result = parse_judge_response(response)
        assert result["score"] == 4
        assert result["explanation"] == "Good response"

    def test_parse_json_in_text(self):
        response = 'Here is my evaluation: {"score": 3, "explanation": "Average"} That is my assessment.'
        result = parse_judge_response(response)
        assert result["score"] == 3

    def test_parse_free_text_score(self):
        response = "The response deserves a score: 5 because it was excellent."
        result = parse_judge_response(response)
        assert result["score"] == 5

    def test_parse_invalid_returns_default(self):
        response = "I cannot evaluate this properly."
        result = parse_judge_response(response)
        assert result["score"] == 3

    def test_parse_out_of_range_score(self):
        response = '{"score": 8, "explanation": "Great"}'
        result = parse_judge_response(response)
        assert result["score"] == 3  # defaults since 8 > 5

    def test_aggregate_score_equal_weights(self):
        scores = {"factuality": 4, "relevance": 5, "coherence": 3}
        result = compute_aggregate_score(scores)
        assert result == 4.0

    def test_aggregate_score_empty(self):
        result = compute_aggregate_score({})
        assert result == 0.0

    def test_aggregate_score_single(self):
        result = compute_aggregate_score({"safety": 5})
        assert result == 5.0


class TestDimensions:
    def test_get_all_dimensions(self):
        dims = get_all_dimensions()
        assert len(dims) == 5
        assert "factuality" in dims
        assert "safety" in dims

    def test_get_dimension_info(self):
        info = get_dimension_info("factuality")
        assert info is not None
        assert info["name"] == "Factuality"
        assert "weight" in info

    def test_unknown_dimension(self):
        info = get_dimension_info("nonexistent")
        assert info is None


class TestJudgePrompts:
    def test_get_prompt_with_expected(self):
        prompt = get_judge_prompt(
            "factuality",
            "What is AI?",
            "AI is artificial intelligence.",
            "AI stands for artificial intelligence.",
        )
        assert "What is AI?" in prompt
        assert "AI is artificial intelligence." in prompt
        assert "Expected Output:" in prompt

    def test_get_prompt_without_expected(self):
        prompt = get_judge_prompt(
            "relevance", "What is AI?", "AI is artificial intelligence."
        )
        assert "What is AI?" in prompt
        assert "Expected Output:" not in prompt

    def test_unknown_dimension_raises(self):
        with pytest.raises(ValueError):
            get_judge_prompt("nonexistent", "test", "test")

    def test_all_dimensions_have_prompts(self):
        for dim in get_all_dimensions():
            prompt = get_judge_prompt(dim, "test input", "test output")
            assert len(prompt) > 50
