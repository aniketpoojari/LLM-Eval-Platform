from backend.logger.logging import get_logger

logger = get_logger(__name__)


class CostService:
    def __init__(self, db):
        self.db = db

    def get_summary(self, days=30):
        row = self.db.fetch_one(
            """
            SELECT
                COALESCE(SUM(estimated_cost), 0) as total_cost,
                COALESCE(SUM(total_tokens), 0) as total_tokens,
                COUNT(*) as total_requests
            FROM cost_tracking
            WHERE created_at >= datetime('now', ? || ' days')
            """,
            [f"-{days}"],
        )

        by_source = self.db.fetch_all(
            """
            SELECT source, COALESCE(SUM(estimated_cost), 0) as cost
            FROM cost_tracking
            WHERE created_at >= datetime('now', ? || ' days')
            GROUP BY source
            """,
            [f"-{days}"],
        )

        daily = self.db.fetch_all(
            """
            SELECT
                DATE(created_at) as date,
                COALESCE(SUM(estimated_cost), 0) as cost,
                COALESCE(SUM(total_tokens), 0) as tokens
            FROM cost_tracking
            WHERE created_at >= datetime('now', ? || ' days')
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            [f"-{days}"],
        )

        return {
            "total_cost": row["total_cost"] if row else 0,
            "total_tokens": row["total_tokens"] if row else 0,
            "total_requests": row["total_requests"] if row else 0,
            "cost_by_source": {r["source"]: r["cost"] for r in by_source},
            "daily_costs": daily,
        }

    def record_cost(
        self,
        cost_id,
        source,
        source_id,
        provider,
        model,
        input_tokens,
        output_tokens,
        cost,
    ):
        self.db.insert(
            "cost_tracking",
            {
                "id": cost_id,
                "source": source,
                "source_id": source_id,
                "provider": provider,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "estimated_cost": round(cost, 6),
            },
        )
