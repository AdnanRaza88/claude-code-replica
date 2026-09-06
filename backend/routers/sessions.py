from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.engine import get_engine

router = APIRouter()


class CreateSessionRequest(BaseModel):
    provider: str = "opencode"
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    workspace: Optional[str] = None
    mode: str = "agent"
    permission_mode: str = "session_allow"


class SessionOut(BaseModel):
    session_id: str
    provider: str
    model: Optional[str] = None
    workspace: Optional[str] = None
    mode: str = "agent"
    permission_mode: str = "session_allow"


class PermissionDecisionBody(BaseModel):
    decision: str


@router.get("")
async def list_sessions():
    engine = get_engine()
    items = []
    for session in engine.list_sessions():
        cfg = session.provider_config
        items.append(
            {
                "session_id": session.session_id,
                "provider": cfg.provider if cfg else "unknown",
                "model": cfg.model if cfg else None,
                "workspace": session.project_root,
                "mode": session.mode,
                "permission_mode": session.permission_mode.value if hasattr(session.permission_mode, "value") else str(session.permission_mode),
                "created_at": session.created_at.isoformat() if session.created_at else None,
            }
        )
    return {"sessions": items, "count": len(items)}


@router.post("", response_model=SessionOut)
async def create_session(body: CreateSessionRequest):
    engine = get_engine()
    session = engine.create_session(
        provider=body.provider,
        model=body.model,
        base_url=body.base_url,
        api_key=body.api_key,
        workspace=body.workspace,
        mode=body.mode,
        permission_mode=body.permission_mode,
    )
    cfg = session.provider_config
    return SessionOut(
        session_id=session.session_id,
        provider=cfg.provider if cfg else body.provider,
        model=cfg.model if cfg else body.model,
        workspace=session.project_root,
        mode=session.mode,
        permission_mode=session.permission_mode.value if hasattr(session.permission_mode, "value") else str(session.permission_mode),
    )


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(session_id: str):
    session = get_engine().get_session(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    cfg = session.provider_config
    return SessionOut(
        session_id=session.session_id,
        provider=cfg.provider if cfg else "unknown",
        model=cfg.model if cfg else None,
        workspace=session.project_root,
        mode=session.mode,
        permission_mode=session.permission_mode.value if hasattr(session.permission_mode, "value") else str(session.permission_mode),
    )


@router.get("/{session_id}/events")
async def list_events(session_id: str, after: int = 0):
    if get_engine().get_session(session_id) is None:
        raise HTTPException(404, "session not found")
    events = get_engine().session_events(session_id, after=after)
    return {"session_id": session_id, "events": events, "count": len(events)}


@router.get("/{session_id}/graph")
async def session_graph(session_id: str):
    if get_engine().get_session(session_id) is None:
        raise HTTPException(404, "session not found")
    return get_engine().session_graph(session_id)


@router.get("/{session_id}/permissions")
async def list_permissions(session_id: str):
    if get_engine().get_session(session_id) is None:
        raise HTTPException(404, "session not found")
    items = get_engine().pending_permissions(session_id)
    return {"session_id": session_id, "pending": items, "count": len(items)}


@router.post("/{session_id}/permissions/{request_id}")
async def decide_permission(session_id: str, request_id: str, body: PermissionDecisionBody):
    if get_engine().get_session(session_id) is None:
        raise HTTPException(404, "session not found")
    try:
        decided = get_engine().decide_permission(session_id, request_id, body.decision)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if decided is None:
        raise HTTPException(404, "permission request not found")
    return decided
