import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.models.pydantic_models import (ABTestCreate, AttackCategory,
                                            EvalDimension, EvaluationCreate,
                                            HealthResponse, RedTeamRunCreate,
                                            TargetCreate)


class TestPydanticModels:
    def test_target_create(self):
        target = TargetCreate(
            name="Test Target",
            api_url="http://localhost:8000/query",
        )
        assert target.name == "Test Target"
        assert target.api_method == "POST"
        assert target.response_path == "response"

    def test_target_create_full(self):
        target = TargetCreate(
            name="Full Target",
            description="Test description",
            api_url="http://localhost:8000/query",
            api_method="POST",
            headers={"Authorization": "Bearer token"},
            request_template='{"prompt": "{{input}}"}',
            response_path="data.response",
        )
        assert target.headers["Authorization"] == "Bearer token"

    def test_evaluation_create(self):
        ev = EvaluationCreate(
            name="Test Eval",
            target_id="test-id",
            queries=[{"input": "What is AI?"}],
        )
        assert len(ev.dimensions) == 5
        assert EvalDimension.FACTUALITY in ev.dimensions

    def test_evaluation_create_custom_dims(self):
        ev = EvaluationCreate(
            name="Custom Eval",
            target_id="test-id",
            dimensions=[EvalDimension.SAFETY, EvalDimension.FACTUALITY],
            queries=[{"input": "test"}],
        )
        assert len(ev.dimensions) == 2

    def test_red_team_run_create(self):
        run = RedTeamRunCreate(
            name="Test Run",
            target_id="test-id",
        )
        assert len(run.categories) == 6
        assert run.max_attacks == 50

    def test_red_team_custom_categories(self):
        run = RedTeamRunCreate(
            name="Focused Run",
            target_id="test-id",
            categories=[AttackCategory.JAILBREAK, AttackCategory.PROMPT_INJECTION],
            max_attacks=20,
        )
        assert len(run.categories) == 2
        assert run.max_attacks == 20

    def test_ab_test_create(self):
        test = ABTestCreate(
            name="A vs B",
            target_a_id="id-a",
            target_b_id="id-b",
            queries=["What is AI?", "Explain ML"],
        )
        assert len(test.dimensions) == 3
        assert len(test.queries) == 2

    def test_health_response(self):
        h = HealthResponse()
        assert h.status == "healthy"
        assert h.version == "1.0.0"


class TestDatabaseManager:
    @pytest.fixture
    def db_path(self, tmp_path):
        return str(tmp_path / "test.db")

    def test_database_init(self, db_path):
        from backend.models.database import DatabaseManager

        db = DatabaseManager(db_path=db_path)
        result = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [r["name"] for r in result]
        assert "targets" in table_names
        assert "evaluations" in table_names
        assert "red_team_runs" in table_names
        assert "ab_experiments" in table_names
        assert "metrics" in table_names
        assert "cost_tracking" in table_names

    def test_crud_operations(self, db_path):
        from backend.models.database import DatabaseManager

        db = DatabaseManager(db_path=db_path)
        db.insert(
            "targets",
            {
                "id": "test-1",
                "name": "Test",
                "api_url": "http://test.com",
                "request_template": '{"q": "{{input}}"}',
            },
        )

        row = db.fetch_one("SELECT * FROM targets WHERE id = ?", ["test-1"])
        assert row["name"] == "Test"

        db.update("targets", {"name": "Updated"}, "id = ?", ["test-1"])
        row = db.fetch_one("SELECT * FROM targets WHERE id = ?", ["test-1"])
        assert row["name"] == "Updated"

        db.delete("targets", "id = ?", ["test-1"])
        row = db.fetch_one("SELECT * FROM targets WHERE id = ?", ["test-1"])
        assert row is None
