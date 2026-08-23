from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


class AgentStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_PERMISSION = "waiting_permission"
    WAITING_CHILDREN = "waiting_children"
    VERIFYING = "verifying"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BudgetState(BaseModel):
    depth: int = 0
    max_depth: int = 4
    children_spawned: int = 0
    max_children: int = 8
    token_used: int = 0
    token_budget: int = 120000
    wall_clock_seconds: float = 0.0
    wall_clock_budget: float = 300.0
    spawn_budget_remaining: int = 64


class VerificationState(BaseModel):
    status: str = "pending"
    checks: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    notes: str = ""


class ArtifactRef(BaseModel):
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kind: str
    path: str | None = None
    content_preview: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: str = "info"
    summary: str
    detail: str | None = None
    source_agent: str | None = None


class AgentState(BaseModel):
    task_id: str
    session_id: str
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str | None = None
    domain: str = "general"
    role: str = "worker"
    objective: str
    context_refs: list[str] = Field(default_factory=list)
    skill_refs: list[str] = Field(default_factory=list)
    tool_refs: list[str] = Field(default_factory=list)
    children: list[str] = Field(default_factory=list)
    depth: int = 0
    budgets: BudgetState = Field(default_factory=BudgetState)
    status: AgentStatus = AgentStatus.CREATED
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    verification: VerificationState = Field(default_factory=VerificationState)
    result_summary: str | None = None
    open_questions: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    permission_state: dict[str, str] = Field(default_factory=dict)
    provider_config_ref: str | None = None
    error: str | None = None

    def can_spawn(self) -> bool:
        return (
            self.depth < self.budgets.max_depth
            and self.budgets.children_spawned < self.budgets.max_children
            and self.budgets.spawn_budget_remaining > 0
            and self.status not in {AgentStatus.CANCELLED, AgentStatus.FAILED}
        )
