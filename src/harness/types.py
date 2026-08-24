from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class Phase(str, Enum):
    THINK = "think"
    REASON = "reason"
    ACT = "act"
    OBSERVE = "observe"
    VERIFY = "verify"
    DONE = "done"
    FAILED = "failed"


class StepKind(str, Enum):
    THOUGHT = "thought"
    REASONING = "reasoning"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    OBSERVATION = "observation"
    VERIFICATION = "verification"
    FINAL = "final"
    ERROR = "error"


class SandboxStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phase: Phase
    kind: StepKind
    content: str = ""
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    tool_output: str | None = None
    success: bool | None = None
    token_hint: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class SandboxTrace(BaseModel):
    """Compact per-agent cognitive trace. Kept short for prompt injection."""

    agent_id: str
    domain: str = "general"
    objective: str = ""
    steps: list[SandboxStep] = Field(default_factory=list)
    max_steps: int = 8
    current_phase: Phase = Phase.THINK
    final_summary: str | None = None
    sources: list[dict[str, Any]] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence: float = 0.0

    def add(
        self,
        phase: Phase,
        kind: StepKind,
        content: str = "",
        tool_name: str | None = None,
        tool_input: dict | None = None,
        tool_output: str | None = None,
        success: bool | None = None,
        metadata: dict | None = None,
    ) -> SandboxStep:
        step = SandboxStep(
            phase=phase,
            kind=kind,
            content=content[:2000],
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=(tool_output or "")[:3000] if tool_output else None,
            success=success,
            metadata=metadata or {},
        )
        self.steps.append(step)
        self.current_phase = phase
        return step

    def recent_text(self, limit: int = 6) -> str:
        """Short rolling summary safe to inject into the next model call."""
        if not self.steps:
            return ""
        lines: list[str] = []
        for s in self.steps[-limit:]:
            prefix = s.phase.value.upper()
            if s.kind == StepKind.TOOL_CALL and s.tool_name:
                lines.append(f"[{prefix}] tool:{s.tool_name}({_short(s.tool_input)})")
            elif s.kind == StepKind.TOOL_RESULT:
                status = "ok" if s.success else "err"
                lines.append(f"[{prefix}] result({status}): {_clip(s.tool_output or s.content, 180)}")
            else:
                lines.append(f"[{prefix}] {_clip(s.content, 220)}")
        return "\n".join(lines)

    def is_budget_exceeded(self) -> bool:
        return len(self.steps) >= self.max_steps


def _clip(text: str, n: int) -> str:
    text = (text or "").strip().replace("\n", " ")
    return text if len(text) <= n else text[: n - 1] + "…"


def _short(obj: Any, n: int = 80) -> str:
    if obj is None:
        return ""
    s = str(obj)
    return s if len(s) <= n else s[: n - 1] + "…"
