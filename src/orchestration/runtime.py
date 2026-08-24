from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Optional

from src.models.agent import AgentState, AgentStatus, BudgetState
from src.models.task import Task, TaskGraph, TaskStatus
from src.models.events import RuntimeEvent, EventType
from src.models.provider import Message, ProviderConfig, ToolSpec
from src.models.permission import PermissionDecision
from src.services.session_service import SessionService, SessionState
from src.services.permission_service import PermissionService
from src.services.event_service import EventService
from src.services.context_service import ContextService
from src.adapters.providers.registry import ProviderRegistry
from src.tools.base import ToolRegistry, ToolResult
from src.orchestration.planner import Planner

try:
    from src.services.skill_service import SkillService
except Exception:  # pragma: no cover
    SkillService = None  # type: ignore

try:
    from src.harness import AgentSandbox, SandboxRegistry, CognitiveLoop
except Exception:  # pragma: no cover
    AgentSandbox = None  # type: ignore
    SandboxRegistry = None  # type: ignore
    CognitiveLoop = None  # type: ignore

PLAN_MODE_ALLOWED_TOOLS = frozenset(
    {"read", "search", "web_search", "web_fetch", "github"}
)
PLAN_MODE_BLOCKED_TOOLS = frozenset({"write", "edit", "bash"})


class AgentRuntime:
    def __init__(
        self,
        session_service: SessionService,
        permission_service: PermissionService,
        event_service: EventService,
        context_service: ContextService,
        provider_registry: ProviderRegistry,
        tool_registry: ToolRegistry,
        get_credential: Optional[Callable[[str], Optional[str]]] = None,
        skill_service=None,
        use_harness: bool = True,
    ):
        self.sessions = session_service
        self.permissions = permission_service
        self.events = event_service
        self.context = context_service
        self.providers = provider_registry
        self.tools = tool_registry
        self.get_credential = get_credential or (lambda _: None)
        self.use_harness = use_harness and CognitiveLoop is not None

        if skill_service is not None:
            self.skills = skill_service
        elif SkillService is not None:
            try:
                self.skills = SkillService()
                self.skills.load_all()
            except Exception:
                self.skills = None
        else:
            self.skills = None

        if self.skills is not None and hasattr(self.context, "set_skill_service"):
            self.context.set_skill_service(self.skills)

        try:
            self.planner = Planner(skill_service=self.skills)
        except TypeError:
            self.planner = Planner()

        self._agents: dict[str, AgentState] = {}
        self._graphs: dict[str, TaskGraph] = {}
        self._cancel_flags: dict[str, bool] = {}
        self._sandboxes = SandboxRegistry() if SandboxRegistry is not None else None

    def _emit(
        self,
        session_id: str,
        event_type: EventType,
        agent_id: str | None = None,
        task_id: str | None = None,
        message: str = "",
        payload: dict | None = None,
        parent_agent_id: str | None = None,
    ) -> None:
        self.events.emit(
            RuntimeEvent(
                event_type=event_type,
                session_id=session_id,
                agent_id=agent_id,
                task_id=task_id,
                parent_agent_id=parent_agent_id,
                message=message,
                payload=payload or {},
            )
        )

    def _is_plan_mode(self, session: SessionState) -> bool:
        return (session.mode or "agent") == "plan"

    def _filter_tools_for_mode(self, session: SessionState, tools: list[str]) -> list[str]:
        if not self._is_plan_mode(session):
            return list(tools)
        return [t for t in tools if t in PLAN_MODE_ALLOWED_TOOLS]

    async def run_task(
        self,
        session_id: str,
        objective: str,
        project_context: str = "",
    ) -> dict[str, Any]:
        session = self.sessions.get(session_id)
        if session is None:
            raise ValueError("unknown session")
        if session.provider_config is None:
            raise ValueError("provider not configured")

        if self._is_plan_mode(session):
            self._emit(
                session_id,
                EventType.THINKING,
                message=f"plan mode active — write/edit/bash blocked; producing plan only",
                payload={"mode": "plan"},
            )

        graph = self.planner.create_graph(session_id, objective)
        self._graphs[session_id] = graph
        self._cancel_flags[session_id] = False

        root = graph.tasks[graph.root_task_id]
        root_agent = self._spawn_agent(session, root, depth=0, parent_id=None)
        self._emit(session_id, EventType.CREATED, root_agent.agent_id, root.task_id, "root agent created")

        result = await self._execute_agent(session, root_agent, root, graph, project_context)

        if self._is_plan_mode(session) and result:
            self.sessions.set_last_plan(session_id, result)
            result = dict(result)
            result["mode"] = "plan"
            result.setdefault("open_questions", [])
            if "plan" not in result and result.get("summary"):
                result["plan"] = result.get("summary")
        return result

    def _spawn_agent(
        self,
        session: SessionState,
        task: Task,
        depth: int,
        parent_id: str | None,
    ) -> AgentState:
        skill_refs = list(task.required_skills or [])
        if not skill_refs and self.skills is not None:
            primary = self.skills.primary_for_domain(task.domain)
            if primary:
                skill_refs = [primary.skill_id]
        role = "orchestrator" if task.domain in ("orchestrator", "planning") and depth == 0 else "worker"
        raw_tools = task.required_tools or self.tools.list_names()
        allowed = self._filter_tools_for_mode(session, list(raw_tools))
        agent = AgentState(
            task_id=task.task_id,
            session_id=session.session_id,
            parent_id=parent_id,
            domain=task.domain,
            role=role,
            objective=task.objective,
            depth=depth,
            budgets=BudgetState(depth=depth),
            skill_refs=skill_refs,
            allowed_tools=allowed,
            provider_config_ref=session.session_id,
            status=AgentStatus.CREATED,
        )
        self._agents[agent.agent_id] = agent
        task.assigned_agent_id = agent.agent_id
        session.active_agent_ids.append(agent.agent_id)
        return agent
