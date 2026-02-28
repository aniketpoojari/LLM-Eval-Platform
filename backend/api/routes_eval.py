import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models.pydantic_models import (EvalResultResponse,
                                            EvaluationCreate,
                                            EvaluationResponse)

router = APIRouter(prefix="/api/evaluations", tags=["Evaluations"])


def get_db():
    from backend.main import db

    return db


def get_eval_service():
    from backend.main import eval_service

    return eval_service


@router.post("", response_model=EvaluationResponse)
async def create_evaluation(request: EvaluationCreate):
    eval_svc = get_eval_service()
    evaluation = await eval_svc.create_evaluation(request)
    return evaluation


@router.get("", response_model=list[EvaluationResponse])
async def list_evaluations():
    db = get_db()
    rows = db.fetch_all("SELECT * FROM evaluations ORDER BY created_at DESC")
    return [EvaluationResponse.from_db(r) for r in rows]


@router.get("/{eval_id}", response_model=EvaluationResponse)
async def get_evaluation(eval_id: str):
    db = get_db()
    row = db.fetch_one("SELECT * FROM evaluations WHERE id = ?", [eval_id])
    if not row:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return EvaluationResponse.from_db(row)


@router.get("/{eval_id}/results", response_model=list[EvalResultResponse])
async def get_evaluation_results(eval_id: str):
    db = get_db()
    rows = db.fetch_all(
        "SELECT * FROM evaluation_results WHERE evaluation_id = ? ORDER BY created_at",
        [eval_id],
    )
    return [EvalResultResponse.from_db(r) for r in rows]


@router.get("/{eval_id}/progress")
async def evaluation_progress(eval_id: str):
    eval_svc = get_eval_service()
    return StreamingResponse(
        eval_svc.stream_progress(eval_id),
        media_type="text/event-stream",
    )


@router.get("/{eval_id}/export")
async def export_evaluation(eval_id: str, format: str = "json"):
    db = get_db()
    evaluation = db.fetch_one("SELECT * FROM evaluations WHERE id = ?", [eval_id])
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    results = db.fetch_all(
        "SELECT * FROM evaluation_results WHERE evaluation_id = ?", [eval_id]
    )

    from backend.utils.export import export_to_csv, export_to_json

    if format == "csv":
        from fastapi.responses import Response

        csv_data = export_to_csv(
            [EvalResultResponse.from_db(r).model_dump() for r in results]
        )
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=eval_{eval_id}.csv"},
        )
    else:
        data = {
            "evaluation": EvaluationResponse.from_db(evaluation).model_dump(),
            "results": [EvalResultResponse.from_db(r).model_dump() for r in results],
        }
        json_data = export_to_json(data)
        from fastapi.responses import Response

        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=eval_{eval_id}.json"
            },
        )
