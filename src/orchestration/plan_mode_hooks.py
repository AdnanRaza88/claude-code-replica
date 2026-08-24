"""F-018 plan mode — install onto AgentRuntime without rewriting the whole module."""
from __future__ import annotations

from typing import Any

from src.models.events import EventType
from src.tools.base import ToolResult

PLAN_MODE_ALLOWED_TOOLS = frozenset(
    {"read", "search", "web_search", "web_fetch", "github"}
)
PLAN_MODE_BLOCKED_TOOLS = frozenset({"write", "edit", "bash"})

_INSTALLED = False


def install(AgentRuntime: type) -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    AgentRuntime.PLAN_MODE_ALLOWED_TOOLS = PLAN_MODE_ALLOWED_TOOLS
    AgentRuntime.PLAN_MODE_BLOCKED_TOOLS = PLAN_MODE_BLOCKED_TOOLS

    def _is_plan_mode(self, session) -> bool:
        return (getattr(session, "mode", None) or "agent") == "plan"

    def _filter_tools_for_mode(self, session, tools: list[str]) -> list[str]:
        if not self._is_plan_mode(session):
            return list(tools)
        return [t for t in tools if t in PLAN_MODE_ALLOWED_TOOLS]

    _orig_spawn = AgentRuntime._spawn_agent
    _orig_invoke = AgentRuntime._invoke_tool
    _orig_run = AgentRuntime.run_task

    def _spawn_agent(self, session, task, depth, parent_id):
        agent = _orig_spawn(self, session, task, depth, parent_id)
        if self._is_plan_mode(session):
            agent.allowed_tools = self._filter_tools_for_mode(
                session, list(agent.allowed_tools or [])
            )
        return agent

    async def _invoke_tool(self, session, agent, tool_name: str, tool_input: dict):
        if self._is_plan_mode(session) and (
            tool_name in PLAN_MODE_BLOCKED_TOOLS
            or tool_name not in PLAN_MODE_ALLOWED_TOOLS
        ):
            msg = (
                f"blocked in plan mode: '{tool_name}' is not allowed. "
                f"Plan mode only permits: {', '.join(sorted(PLAN_MODE_ALLOWED_TOOLS))}. "
                "Switch to agent mode to execute writes."
            )
            self._emit(
                session.session_id,
                EventType.TOOL_PERMISSION_REQUESTED,
                agent.agent_id,
                agent.task_id,
                msg,
                {"tool": tool_name, "mode": "plan", "blocked": True},
            )
            return ToolResult(success=False, error=msg)
        return await _orig_invoke(self, session, agent, tool_name, tool_input)

    async def run_task(self, session_id: str, objective: str, project_context: str = ""):
        session = self.sessions.get(session_id)
        if session is not None and self._is_plan_mode(session):
            self._emit(
                session_id,
                EventType.THINKING,
                message="plan mode active — write/edit/bash blocked; producing plan only",
                payload={"mode": "plan"},
            )
        result = await _orig_run(self, session_id, objective, project_context)
        if session is not None and self._is_plan_mode(session) and result:
            if hasattr(self.sessions, "set_last_plan"):
                self.sessions.set_last_plan(session_id, result)
            result = dict(result)
            result["mode"] = "plan"
            result.setdefault("open_questions", [])
            if "plan" not in result and result.get("summary"):
                result["plan"] = result.get("summary")
        return result

    AgentRuntime._is_plan_mode = _is_plan_mode
    AgentRuntime._filter_tools_for_mode = _filter_tools_for_mode
    AgentRuntime._spawn_agent = _spawn_agent
    AgentRuntime._invoke_tool = _invoke_tool
    AgentRuntime.run_task = run_task
