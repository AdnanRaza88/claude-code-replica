"""F-018 plan mode + F-033 SDD hints — install onto AgentRuntime."""
from __future__ import annotations

from src.models.events import EventType
from src.tools.base import ToolResult

PLAN_MODE_ALLOWED_TOOLS = frozenset(
    {"read", "search", "web_search", "web_fetch", "github", "write", "edit"}
)
# write/edit allowed only for spec paths when plan mode (checked in invoke)
PLAN_MODE_BLOCKED_TOOLS = frozenset({"bash"})

_SPEC_PATH_MARKERS = (".agentforge/specs/", ".agentforge/BIBLE.md", "/INTENT.md", "/PRD.md", "/TRD.md", "/WAVES.md", "/BIBLE.md")

_INSTALLED = False

_SDD_PLAN_HINT = (
    "\n\n[PLAN MODE + SDD]\n"
    "Produce short contracts only: Intent → PRD-lite → TRD-lite → WAVES → BIBLE under "
    ".agentforge/specs/<slug>/. No production feature code. No bash. "
    "Acceptance lines must be testable. Parallel waves only after bible lock.\n"
)


def _path_is_spec_artifact(tool_input: dict) -> bool:
    path = str(
        tool_input.get("path")
        or tool_input.get("file")
        or tool_input.get("file_path")
        or tool_input.get("target")
        or ""
    )
    return any(m in path.replace("\\", "/") for m in _SPEC_PATH_MARKERS)


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
            # Prefer SDD skill in plan mode
            skills = list(agent.skill_refs or [])
            if "sdd/sdd" not in skills:
                skills.insert(0, "sdd/sdd")
            agent.skill_refs = skills
        return agent

    async def _invoke_tool(self, session, agent, tool_name: str, tool_input: dict):
        if self._is_plan_mode(session):
            if tool_name == "bash":
                msg = (
                    "blocked in plan mode: 'bash' is not allowed. "
                    "Write specs under .agentforge/specs/ only; switch to agent mode to execute."
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
            if tool_name in ("write", "edit") and not _path_is_spec_artifact(tool_input):
                msg = (
                    f"blocked in plan mode: '{tool_name}' only allowed for "
                    ".agentforge/specs/* and .agentforge/BIBLE.md. "
                    "Switch to agent mode for other files."
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
            if tool_name not in PLAN_MODE_ALLOWED_TOOLS:
                msg = (
                    f"blocked in plan mode: '{tool_name}' is not allowed. "
                    f"Permitted: {', '.join(sorted(PLAN_MODE_ALLOWED_TOOLS))}."
                )
                return ToolResult(success=False, error=msg)
        return await _orig_invoke(self, session, agent, tool_name, tool_input)

    async def run_task(self, session_id: str, objective: str, project_context: str = ""):
        session = self.sessions.get(session_id)
        if session is not None and self._is_plan_mode(session):
            self._emit(
                session_id,
                EventType.THINKING,
                message="plan mode + SDD — specs only; bash blocked; write limited to .agentforge/specs",
                payload={"mode": "plan", "sdd": True},
            )
            if project_context:
                project_context = project_context + _SDD_PLAN_HINT
            else:
                project_context = _SDD_PLAN_HINT.strip()

        # Prefer planner aware of mode when create_graph supports it
        planner = getattr(self, "planner", None)
        if planner is not None and hasattr(planner, "create_graph"):
            _orig_cg = planner.create_graph

            def _cg(sid, obj, **kwargs):
                kwargs.setdefault("mode", getattr(session, "mode", "agent") if session else "agent")
                return _orig_cg(sid, obj, **kwargs)

            # temporary bind only if signature allows — avoid break if positional only
            try:
                import inspect

                params = inspect.signature(_orig_cg).parameters
                if "mode" in params:
                    planner.create_graph = _cg  # type: ignore
            except Exception:
                pass

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
