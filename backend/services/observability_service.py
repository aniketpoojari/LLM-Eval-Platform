from backend.logger.logging import get_logger
from backend.models.pydantic_models import CostSummary, MetricSummary
from backend.observability.aggregator import MetricsAggregator
from backend.services.cost_service import CostService

logger = get_logger(__name__)


class ObservabilityService:
    def __init__(self, db):
        self.db = db
        self.aggregator = MetricsAggregator(db)
        self.cost_service = CostService(db)

    def get_summary(self):
        evals = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM evaluations WHERE status = 'completed'"
        )
        red_team = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM red_team_runs WHERE status = 'completed'"
        )
        ab_tests = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM ab_experiments WHERE status = 'completed'"
        )

        total_queries = self.db.fetch_one("""
            SELECT
                (SELECT COALESCE(SUM(completed_queries), 0) FROM evaluations) +
                (SELECT COALESCE(SUM(completed_attacks), 0) FROM red_team_runs) +
                (SELECT COALESCE(SUM(completed_queries), 0) FROM ab_experiments) as total
            """)

        latency = self.db.fetch_one(
            "SELECT AVG(value) as avg FROM metrics WHERE metric_type = 'latency_ms'"
        )

        cost_data = self.db.fetch_one(
            "SELECT COALESCE(SUM(total_tokens), 0) as tokens, COALESCE(SUM(estimated_cost), 0) as cost FROM cost_tracking"
        )

        return MetricSummary(
            total_evaluations=evals["count"] if evals else 0,
            total_red_team_runs=red_team["count"] if red_team else 0,
            total_ab_tests=ab_tests["count"] if ab_tests else 0,
            total_queries_processed=total_queries["total"] if total_queries else 0,
            avg_latency_ms=(
                round(latency["avg"], 2) if latency and latency["avg"] else None
            ),
            total_tokens=cost_data["tokens"] if cost_data else 0,
            total_cost=round(cost_data["cost"], 4) if cost_data else 0,
        )

    def get_token_timeseries(self, days=30):
        return self.aggregator.get_token_timeseries(days)

    def get_cost_summary(self, days=30):
        data = self.cost_service.get_summary(days)
        return CostSummary(**data)

    def get_latency_timeseries(self, days=30):
        return self.aggregator.get_latency_timeseries(days)

    def get_score_trends(self, days=30):
        return self.aggregator.get_score_trends(days)
