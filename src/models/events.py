from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class EventType(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    STARTED = "started"
    TOOL_PERMISSION_REQUESTED = "tool_permission_requested"
    TOOL_STARTED = "tool_started"
    TOOL_FINISHED = "tool_finished"
    CHILD_SPAWNED = "child_spawned"
    CHILD_FINISHED = "child_finished"
    VERIFICATION_STARTED = "verification_started"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    BUDGET_WARNING = "budget_warning"
    CONTEXT_COMPACTED = "context_compacted"
    RECOVERY = "recovery"


class RuntimeEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    session_id: str
    task_id: str | None = None
    agent_id: str | None = None
    parent_agent_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
