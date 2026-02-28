from backend.logger.logging import get_logger

logger = get_logger(__name__)


class MetricsAggregator:
    def __init__(self, db):
        self.db = db

    def get_latency_timeseries(self, days=30):
        rows = self.db.fetch_all(
            """
            SELECT
                DATE(created_at) as date,
                AVG(value) as avg_latency,
                MIN(value) as min_latency,
                MAX(value) as max_latency,
                COUNT(*) as count
            FROM metrics
            WHERE metric_type = 'latency_ms'
              AND created_at >= datetime('now', ? || ' days')
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            [f"-{days}"],
        )
        return rows

    def get_score_trends(self, days=30):
        rows = self.db.fetch_all(
            """
            SELECT
                DATE(e.created_at) as date,
                AVG(e.avg_score) as avg_score,
                COUNT(*) as eval_count
            FROM evaluations e
            WHERE e.status = 'completed'
              AND e.created_at >= datetime('now', ? || ' days')
            GROUP BY DATE(e.created_at)
            ORDER BY date
            """,
            [f"-{days}"],
        )
        return rows

    def get_error_rate(self, days=30):
        total = self.db.fetch_one(
            """
            SELECT COUNT(*) as total
            FROM metrics
            WHERE created_at >= datetime('now', ? || ' days')
            """,
            [f"-{days}"],
        )

        errors = self.db.fetch_one(
            """
            SELECT COUNT(*) as errors
            FROM metrics
            WHERE metric_type = 'error'
              AND created_at >= datetime('now', ? || ' days')
            """,
            [f"-{days}"],
        )

        total_count = total["total"] if total else 0
        error_count = errors["errors"] if errors else 0

        return {
            "total_requests": total_count,
            "errors": error_count,
            "error_rate": round(error_count / total_count, 4) if total_count > 0 else 0,
        }

    def get_token_timeseries(self, days=30):
        rows = self.db.fetch_all(
            """
            SELECT
                DATE(created_at) as date,
                COALESCE(SUM(input_tokens), 0) as input_tokens,
                COALESCE(SUM(output_tokens), 0) as output_tokens,
                COALESCE(SUM(total_tokens), 0) as total_tokens,
                COALESCE(SUM(estimated_cost), 0) as cost
            FROM cost_tracking
            WHERE created_at >= datetime('now', ? || ' days')
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            [f"-{days}"],
        )
        return rows
