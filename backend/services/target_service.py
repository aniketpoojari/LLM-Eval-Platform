import json

from backend.logger.logging import get_logger
from backend.utils.http_client import AsyncHTTPClient

logger = get_logger(__name__)


class TargetService:
    def __init__(self, db):
        self.db = db
        self.http_client = AsyncHTTPClient()

    def get_target(self, target_id):
        return self.db.fetch_one("SELECT * FROM targets WHERE id = ?", [target_id])

    async def send_query(self, target, input_text):
        headers = json.loads(target.get("headers", "{}"))
        template = target.get("request_template", '{"query": "{{input}}"}')
        body_str = template.replace("{{input}}", input_text)

        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            body = {"query": input_text}

        response = await self.http_client.send_request(
            method=target.get("api_method", "POST"),
            url=target["api_url"],
            headers=headers,
            json_body=body,
        )

        output = None
        if response.get("json"):
            path_parts = target.get("response_path", "response").split(".")
            data = response["json"]
            for part in path_parts:
                if isinstance(data, dict):
                    data = data.get(part)
                else:
                    data = None
                    break
            output = str(data) if data is not None else str(response["json"])
        else:
            output = response.get("body", "")

        return {
            "output": output,
            "latency_ms": response.get("latency_ms", 0),
            "status_code": response.get("status_code", 0),
            "error": response.get("error"),
        }
