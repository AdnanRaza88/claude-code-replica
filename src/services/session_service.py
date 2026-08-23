from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

from src.models.provider import ProviderConfig
from src.models.permission import PermissionMode


class SessionState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider_config: ProviderConfig | None = None
    permission_mode: PermissionMode = PermissionMode.ASK
    mode: str = "agent"
    project_root: str | None = None
    active_agent_ids: list[str] = Field(default_factory=list)
    root_task_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    cancelled: bool = False


class SessionService:
    def __init__(self):
        self._sessions: dict[str, SessionState] = {}

    def create(
        self,
        provider_config: ProviderConfig | None = None,
        permission_mode: PermissionMode = PermissionMode.ASK,
        project_root: str | None = None,
    ) -> SessionState:
        session = SessionState(
            provider_config=provider_config,
            permission_mode=permission_mode,
            project_root=project_root,
        )
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def update_provider(self, session_id: str, config: ProviderConfig) -> SessionState | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        session.provider_config = config
        return session

    def cancel(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.cancelled = True

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
