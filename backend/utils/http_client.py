import time

import httpx

from backend.logger.logging import get_logger

logger = get_logger(__name__)


class AsyncHTTPClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    async def send_request(
        self, method, url, headers=None, json_body=None, params=None
    ):
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers or {},
                    json=json_body,
                    params=params,
                )
                latency_ms = (time.time() - start_time) * 1000

                return {
                    "status_code": response.status_code,
                    "body": response.text,
                    "json": (
                        response.json()
                        if response.headers.get("content-type", "").startswith(
                            "application/json"
                        )
                        else None
                    ),
                    "latency_ms": round(latency_ms, 2),
                    "headers": dict(response.headers),
                }
        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Request timeout: {method} {url} ({latency_ms:.0f}ms)")
            return {
                "status_code": 408,
                "body": "Request timeout",
                "json": None,
                "latency_ms": round(latency_ms, 2),
                "headers": {},
                "error": "timeout",
            }
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Request error: {method} {url} -> {str(e)}")
            return {
                "status_code": 0,
                "body": str(e),
                "json": None,
                "latency_ms": round(latency_ms, 2),
                "headers": {},
                "error": str(e),
            }

    async def post(self, url, json_body=None, headers=None):
        return await self.send_request(
            "POST", url, headers=headers, json_body=json_body
        )

    async def get(self, url, params=None, headers=None):
        return await self.send_request("GET", url, headers=headers, params=params)
