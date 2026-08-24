from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid

from src.harness.types import Phase, StepKind, SandboxTrace, SandboxStep


class AgentSandbox(BaseModel):
    """
    Per-agent isolated cognitive sandbox.

    Inspired by DeepSeek Harness scoped context:
    - every agent owns its own trace, scratch, tool allowlist, and context refs
    - no shared mutable state between agents (prevents cross-talk / "crazy" mixing)
    - compact enough that recent_text() can be injected without blowing the window
    """

    sandbox_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    session_id: str
    domain: str = "general"
    role: str = "worker"
    objective: str = ""
    depth: int = 0

    # Isolation boundaries
    allowed_tools: list[str] = Field(default_factory=list)
    skill_refs: list[str] = Field(default_factory=list)
    context_refs: list[str] = Field(default_factory=list)

    # Working memory (private to this agent)
    scratch: dict[str, Any] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)

    # Cognitive trace
    trace: SandboxTrace | None = None
    max_steps: int = 8
    enable_verify: bool = True

    # Runtime flags
    cancelled: bool = False
    error: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.trace is None:
            self.trace = SandboxTrace(
                agent_id=self.agent_id,
                domain=self.domain,
                objective=self.objective,
                max_steps=self.max_steps,
            )

    def think(self, content: str, metadata: dict | None = None) -> SandboxStep:
        assert self.trace is not None
        return self.trace.add(Phase.THINK, StepKind.THOUGHT, content=content, metadata=metadata)

    def reason(self, content: str, metadata: dict | None = None) -> SandboxStep:
        assert self.trace is not None
        return self.trace.add(Phase.REASON, StepKind.REASONING, content=content, metadata=metadata)

    def act_tool(
        self,
        tool_name: str,
        tool_input: dict,
        metadata: dict | None = None,
    ) -> SandboxStep:
        assert self.trace is not None
        return self.trace.add(
            Phase.ACT,
            StepKind.TOOL_CALL,
            content=f"call {tool_name}",
            tool_name=tool_name,
            tool_input=tool_input,
            metadata=metadata,
        )

    def observe(
        self,
        tool_name: str,
        output: str,
        success: bool,
        metadata: dict | None = None,
    ) -> SandboxStep:
        assert self.trace is not None
        return self.trace.add(
            Phase.OBSERVE,
            StepKind.TOOL_RESULT,
            content=output[:500],
            tool_name=tool_name,
            tool_output=output,
            success=success,
            metadata=metadata,
        )

    def verify(self, content: str, confidence: float = 0.0, metadata: dict | None = None) -> SandboxStep:
        assert self.trace is not None
        self.trace.confidence = max(0.0, min(1.0, confidence))
        return self.trace.add(
            Phase.VERIFY,
            StepKind.VERIFICATION,
            content=content,
            metadata=metadata or {"confidence": confidence},
        )

    def finalize(self, summary: str, sources: list[dict] | None = None) -> SandboxStep:
        assert self.trace is not None
        self.trace.final_summary = summary
        if sources:
            self.trace.sources = sources
        return self.trace.add(Phase.DONE, StepKind.FINAL, content=summary[:1500])

    def fail(self, message: str) -> SandboxStep:
        assert self.trace is not None
        self.error = message
        return self.trace.add(Phase.FAILED, StepKind.ERROR, content=message)

    def note(self, text: str) -> None:
        self.notes.append(text[:500])
        if len(self.notes) > 20:
            self.notes = self.notes[-20:]

    def set_scratch(self, key: str, value: Any) -> None:
        self.scratch[key] = value

    def get_scratch(self, key: str, default: Any = None) -> Any:
        return self.scratch.get(key, default)

    def budget_ok(self) -> bool:
        if self.cancelled or self.error:
            return False
        assert self.trace is not None
        return not self.trace.is_budget_exceeded()

    def recent_context(self, limit: int = 6) -> str:
        assert self.trace is not None
        return self.trace.recent_text(limit=limit)

    def prompt_block(self) -> str:
        """Small system-side block describing this sandbox's private state."""
        parts = [
            f"[Sandbox {self.sandbox_id[:8]} | domain={self.domain} | role={self.role}]",
            f"Objective: {self.objective[:300]}",
        ]
        if self.notes:
            parts.append("Private notes:\n- " + "\n- ".join(self.notes[-5:]))
        recent = self.recent_context(5)
        if recent:
            parts.append("Recent steps:\n" + recent)
        return "\n".join(parts)


class SandboxRegistry:
    """Session-scoped registry: one sandbox per agent_id. Never shared across agents."""

    def __init__(self) -> None:
        self._by_agent: dict[str, AgentSandbox] = {}

    def create(
        self,
        agent_id: str,
        session_id: str,
        domain: str,
        objective: str,
        role: str = "worker",
        depth: int = 0,
        allowed_tools: Optional[list[str]] = None,
        skill_refs: Optional[list[str]] = None,
        max_steps: int = 8,
        enable_verify: bool = True,
    ) -> AgentSandbox:
        sb = AgentSandbox(
            agent_id=agent_id,
            session_id=session_id,
            domain=domain,
            role=role,
            objective=objective,
            depth=depth,
            allowed_tools=list(allowed_tools or []),
            skill_refs=list(skill_refs or []),
            max_steps=max_steps,
            enable_verify=enable_verify,
        )
        self._by_agent[agent_id] = sb
        return sb

    def get(self, agent_id: str) -> AgentSandbox | None:
        return self._by_agent.get(agent_id)

    def remove(self, agent_id: str) -> None:
        self._by_agent.pop(agent_id, None)

    def clear_session(self, session_id: str) -> None:
        to_drop = [aid for aid, sb in self._by_agent.items() if sb.session_id == session_id]
        for aid in to_drop:
            del self._by_agent[aid]
