import json
import uuid

from fastapi import APIRouter, HTTPException

from backend.models.pydantic_models import (TargetCreate, TargetResponse,
                                            TargetTestRequest,
                                            TargetTestResponse)
from backend.utils.http_client import AsyncHTTPClient

router = APIRouter(prefix="/api/targets", tags=["Targets"])

http_client = AsyncHTTPClient()


def get_db():
    from backend.main import db

    return db


@router.post("", response_model=TargetResponse)
async def create_target(target: TargetCreate):
    db = get_db()
    target_id = str(uuid.uuid4())
    db.insert(
        "targets",
        {
            "id": target_id,
            "name": target.name,
            "description": target.description,
            "api_url": target.api_url,
            "api_method": target.api_method,
            "headers": json.dumps(target.headers),
            "request_template": target.request_template,
            "response_path": target.response_path,
        },
    )
    row = db.fetch_one("SELECT * FROM targets WHERE id = ?", [target_id])
    return TargetResponse.from_db(row)


@router.get("", response_model=list[TargetResponse])
async def list_targets():
    db = get_db()
    rows = db.fetch_all("SELECT * FROM targets ORDER BY created_at DESC")
    return [TargetResponse.from_db(r) for r in rows]


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(target_id: str):
    db = get_db()
    row = db.fetch_one("SELECT * FROM targets WHERE id = ?", [target_id])
    if not row:
        raise HTTPException(status_code=404, detail="Target not found")
    return TargetResponse.from_db(row)


@router.put("/{target_id}", response_model=TargetResponse)
async def update_target(target_id: str, target: TargetCreate):
    db = get_db()
    existing = db.fetch_one("SELECT * FROM targets WHERE id = ?", [target_id])
    if not existing:
        raise HTTPException(status_code=404, detail="Target not found")
    db.update(
        "targets",
        {
            "name": target.name,
            "description": target.description,
            "api_url": target.api_url,
            "api_method": target.api_method,
            "headers": json.dumps(target.headers),
            "request_template": target.request_template,
            "response_path": target.response_path,
            "updated_at": "datetime('now')",
        },
        "id = ?",
        [target_id],
    )
    row = db.fetch_one("SELECT * FROM targets WHERE id = ?", [target_id])
    return TargetResponse.from_db(row)


@router.delete("/{target_id}")
async def delete_target(target_id: str):
    db = get_db()
    existing = db.fetch_one("SELECT * FROM targets WHERE id = ?", [target_id])
    if not existing:
        raise HTTPException(status_code=404, detail="Target not found")
    db.delete("targets", "id = ?", [target_id])
    return {"message": "Target deleted"}


@router.post("/{target_id}/test", response_model=TargetTestResponse)
async def test_target(target_id: str, request: TargetTestRequest):
    db = get_db()
    target = db.fetch_one("SELECT * FROM targets WHERE id = ?", [target_id])
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    headers = json.loads(target["headers"])
    template = target["request_template"]
    body_str = template.replace("{{input}}", request.input_text)

    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        body = {"query": request.input_text}

    result = await http_client.send_request(
        method=target["api_method"],
        url=target["api_url"],
        headers=headers,
        json_body=body,
    )

    response_text = None
    if result.get("json"):
        path_parts = target["response_path"].split(".")
        data = result["json"]
        for part in path_parts:
            if isinstance(data, dict):
                data = data.get(part)
            else:
                data = None
                break
        response_text = str(data) if data is not None else str(result["json"])
    else:
        response_text = result.get("body", "")

    return TargetTestResponse(
        success=200 <= result["status_code"] < 300,
        status_code=result["status_code"],
        response_text=response_text[:2000] if response_text else None,
        latency_ms=result["latency_ms"],
        error=result.get("error"),
    )
