import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.red_team.attack_library import (ATTACK_LIBRARY,
                                             get_attack_count_by_category,
                                             get_attacks_by_category,
                                             get_attacks_by_subcategory,
                                             sample_attacks)
from backend.red_team.categories import ATTACK_CATEGORIES, get_all_categories


class TestAttackLibrary:
    def test_library_has_200_plus_attacks(self):
        assert len(ATTACK_LIBRARY) >= 200

    def test_all_attacks_have_required_fields(self):
        for attack in ATTACK_LIBRARY:
            assert "name" in attack, f"Missing name in {attack}"
            assert "category" in attack, f"Missing category in {attack}"
            assert "input" in attack, f"Missing input in {attack}"
            assert len(attack["input"]) > 10, f"Input too short in {attack['name']}"

    def test_all_categories_have_attacks(self):
        counts = get_attack_count_by_category()
        for cat in ATTACK_CATEGORIES:
            assert counts.get(cat, 0) > 0, f"No attacks for category: {cat}"

    def test_filter_by_category(self):
        injection = get_attacks_by_category("prompt_injection")
        assert len(injection) >= 30
        for a in injection:
            assert a["category"] == "prompt_injection"

    def test_filter_by_subcategory(self):
        attacks = get_attacks_by_subcategory("prompt_injection", "direct_override")
        assert len(attacks) >= 5
        for a in attacks:
            assert a["subcategory"] == "direct_override"

    def test_sample_attacks_limits(self):
        sampled = sample_attacks(max_per_category=5)
        categories_seen = set(a["category"] for a in sampled)
        assert len(categories_seen) == 6
        for cat in categories_seen:
            cat_count = sum(1 for a in sampled if a["category"] == cat)
            assert cat_count <= 5

    def test_sample_specific_categories(self):
        sampled = sample_attacks(categories=["jailbreak", "hallucination"])
        categories_seen = set(a["category"] for a in sampled)
        assert categories_seen == {"jailbreak", "hallucination"}

    def test_attack_count_breakdown(self):
        counts = get_attack_count_by_category()
        total = sum(counts.values())
        assert total == len(ATTACK_LIBRARY)


class TestCategories:
    def test_six_categories(self):
        assert len(ATTACK_CATEGORIES) == 6

    def test_get_all_categories_format(self):
        cats = get_all_categories()
        assert len(cats) == 6
        for c in cats:
            assert "id" in c
            assert "name" in c
            assert "description" in c
            assert "subcategories" in c
            assert "severity" in c

    def test_categories_have_subcategories(self):
        for cat_id, cat in ATTACK_CATEGORIES.items():
            assert len(cat["subcategories"]) >= 4, f"Too few subcategories for {cat_id}"

    def test_severity_levels(self):
        valid_levels = {"critical", "high", "medium", "low"}
        for cat in ATTACK_CATEGORIES.values():
            assert cat["severity"] in valid_levels
