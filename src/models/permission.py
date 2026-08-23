from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class PermissionMode(str, Enum):
    ASK = "ask"
    SESSION_ALLOW = "session_allow"
    DENY = "deny"


class PermissionDecision(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"


class PermissionRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    agent_id: str
    tool_name: str
    tool_input: dict[str, Any] = Field(default_factory=dict)
    risk: str = "medium"
    reason: str = ""
    decision: PermissionDecision = PermissionDecision.PENDING
    decided_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
