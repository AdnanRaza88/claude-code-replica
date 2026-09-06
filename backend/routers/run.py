from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.engine import get_engine

router = APIRouter()


class RunRequest(BaseModel):
    session_id: str
    objective: str = Field(..., min_length=1)
    max_agents: int = 8
    plan_only: bool = False


class RunResponse(BaseModel):
    session_id: str
    status: str
    message: str
    task_id: Optional[str] = None
    detail: Optional[dict[str, Any]] = None


@router.post("", response_model=RunResponse)
async def run_task(body: RunRequest):
    engine = get_engine()
    session = engine.get_session(body.session_id)
    if session is None:
        raise HTTPException(404, "session not found")
    if session.provider_config is None:
        raise HTTPException(400, "provider not configured")

    try:
        result = await engine.run(body.session_id, body.objective, plan_only=body.plan_only)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"run failed: {exc}") from exc

    return RunResponse(
        session_id=body.session_id,
        status="completed",
        message="run finished",
        task_id=session.root_task_id,
        detail=result if isinstance(result, dict) else {"result": result},
    )
