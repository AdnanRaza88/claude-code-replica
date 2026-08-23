from __future__ import annotations

from typing import Callable, Awaitable
from src.models.permission import (
    PermissionMode,
    PermissionDecision,
    PermissionRequest,
)


class PermissionService:
    def __init__(self, default_mode: PermissionMode = PermissionMode.ASK):
        self.default_mode = default_mode
        self._session_allows: dict[str, set[str]] = {}
        self._pending: dict[str, PermissionRequest] = {}
        self._decision_callbacks: dict[str, Callable[[PermissionDecision], Awaitable[None]]] = {}

    def set_mode(self, mode: PermissionMode) -> None:
        self.default_mode = mode

    def allow_for_session(self, session_id: str, tool_name: str) -> None:
        self._session_allows.setdefault(session_id, set()).add(tool_name)

    def is_session_allowed(self, session_id: str, tool_name: str) -> bool:
        return tool_name in self._session_allows.get(session_id, set())

    def request(
        self,
        session_id: str,
        agent_id: str,
        tool_name: str,
        tool_input: dict,
        risk: str = "medium",
        reason: str = "",
    ) -> PermissionRequest:
        if self.default_mode == PermissionMode.DENY:
            req = PermissionRequest(
                session_id=session_id,
                agent_id=agent_id,
                tool_name=tool_name,
                tool_input=tool_input,
                risk=risk,
                reason=reason,
                decision=PermissionDecision.DENIED,
            )
            return req

        if risk == "low" or tool_name in ("github", "read", "search", "web_search", "web_fetch"):
            req = PermissionRequest(
                session_id=session_id,
                agent_id=agent_id,
                tool_name=tool_name,
                tool_input=tool_input,
                risk=risk,
                reason=reason,
                decision=PermissionDecision.APPROVED,
            )
            return req

        if self.default_mode == PermissionMode.SESSION_ALLOW or self.is_session_allowed(
            session_id, tool_name
        ):
            req = PermissionRequest(
                session_id=session_id,
                agent_id=agent_id,
                tool_name=tool_name,
                tool_input=tool_input,
                risk=risk,
                reason=reason,
                decision=PermissionDecision.APPROVED,
            )
            return req

        req = PermissionRequest(
            session_id=session_id,
            agent_id=agent_id,
            tool_name=tool_name,
            tool_input=tool_input,
            risk=risk,
            reason=reason,
        )
        self._pending[req.request_id] = req
        return req

    def decide(self, request_id: str, decision: PermissionDecision) -> PermissionRequest | None:
        req = self._pending.pop(request_id, None)
        if req is None:
            return None
        req.decision = decision
        from datetime import datetime, timezone
        req.decided_at = datetime.now(timezone.utc)
        if decision == PermissionDecision.APPROVED:
            self.allow_for_session(req.session_id, req.tool_name)
        return req

    def get_pending(self, session_id: str) -> list[PermissionRequest]:
        return [r for r in self._pending.values() if r.session_id == session_id]

    def clear_session(self, session_id: str) -> None:
        self._session_allows.pop(session_id, None)
        to_drop = [k for k, v in self._pending.items() if v.session_id == session_id]
        for k in to_drop:
            del self._pending[k]
