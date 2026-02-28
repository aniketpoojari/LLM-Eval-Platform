import uuid

from backend.logger.logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    def __init__(self, db):
        self.db = db

    def record_metric(self, source, source_id, metric_type, value, metadata=None):
        import json

        self.db.insert(
            "metrics",
            {
                "id": str(uuid.uuid4()),
                "source": source,
                "source_id": source_id,
                "metric_type": metric_type,
                "value": value,
                "metadata": json.dumps(metadata or {}),
            },
        )

    def record_latency(self, source, source_id, latency_ms):
        self.record_metric(source, source_id, "latency_ms", latency_ms)

    def record_score(self, source, source_id, score):
        self.record_metric(source, source_id, "score", score)

    def record_error(self, source, source_id, error_msg=None):
        self.record_metric(source, source_id, "error", 1.0, {"message": error_msg})
