from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Awaitable

from src.models.agent import AgentState, AgentStatus, BudgetState
from src.models.task import Task, TaskGraph, TaskStatus
from src.models.events import RuntimeEvent, EventType
from src.models.provider import Message, ProviderConfig, ToolSpec
from src.models.permission import PermissionDecision
from src.services.session_service import SessionService, SessionState
from src.services.permission_service import PermissionService
from src.services.event_service import EventService
from src.services.context_service import ContextService
from src.services.skill_service import SkillService
from src.adapters.providers.registry import ProviderRegistry
from src.tools.base import ToolRegistry, ToolResult
from src.orchestration.planner import Planner


class AgentRuntime:
    def __init__(
        self,
        session_service: SessionService,
        permission_service: PermissionService,
        event_service: EventService,
        context_service: ContextService,
        provider_registry: ProviderRegistry,
        tool_registry: ToolRegistry,
        get_credential: Callable[[str], str | None] | None = None,
        skill_service: SkillService | None = None,
    ):
        self.sessions = session_service
        self.permissions = permission_service
        self.events = event_service
        self.context = context_service
        self.providers = provider_registry
        self.tools = tool_registry
        self.get_credential = get_credential or (lambda _: None)
        self.skills = skill_service or SkillService()
        if skill_service is None:
            self.skills.load_all()
        self.context.set_skill_service(self.skills)
        self.planner = Planner(skill_service=self.skills)
        self._agents: dict[str, AgentState] = {}
        self._graphs: dict[str, TaskGraph] = {}
        self._cancel_flags: dict[str, bool] = {}

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

        graph = self.planner.create_graph(session_id, objective)
        self._graphs[session_id] = graph
        self._cancel_flags[session_id] = False

        root = graph.tasks[graph.root_task_id]
        root_agent = self._spawn_agent(session, root, depth=0, parent_id=None)
        self._emit(session_id, EventType.CREATED, root_agent.agent_id, root.task_id, "root agent created")

        result = await self._execute_agent(session, root_agent, root, graph, project_context)
        return result

    def _spawn_agent(
        self,
        session: SessionState,
        task: Task,
        depth: int,
        parent_id: str | None,
    ) -> AgentState:
        skill_refs = list(task.required_skills or [])
        if not skill_refs and self.skills:
            primary = self.skills.primary_for_domain(task.domain)
            if primary:
                skill_refs = [primary.skill_id]
        role = "orchestrator" if task.domain in ("orchestrator", "planning") and depth == 0 else "worker"
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
            allowed_tools=task.required_tools or self.tools.list_names(),
            provider_config_ref=session.session_id,
            status=AgentStatus.CREATED,
        )
        self._agents[agent.agent_id] = agent
        task.assigned_agent_id = agent.agent_id
        session.active_agent_ids.append(agent.agent_id)
        return agent

    async def _execute_agent(
        self,
        session: SessionState,
        agent: AgentState,
        task: Task,
        graph: TaskGraph,
        project_context: str,
    ) -> dict[str, Any]:
        if self._cancel_flags.get(session.session_id):
            agent.status = AgentStatus.CANCELLED
            self._emit(session.session_id, EventType.CANCELLED, agent.agent_id, task.task_id)
            return {"status": "cancelled", "summary": "cancelled"}

        agent.status = AgentStatus.RUNNING
        task.status = TaskStatus.RUNNING
        self._emit(session.session_id, EventType.STARTED, agent.agent_id, task.task_id, "agent started")

        pack = self.context.build_pack(
            domain=agent.domain,
            project_context=project_context,
            skill_ids=agent.skill_refs or task.required_skills,
            tool_contracts=self.tools.specs_for(agent.allowed_tools),
        )
        agent.context_refs = pack.metadata.get("context_refs", [])
        agent.skill_refs = pack.skill_ids or agent.skill_refs

        children = [t for t in graph.tasks.values() if t.parent_task_id == task.task_id]
        if children and agent.can_spawn():
            return await self._run_with_children(session, agent, task, graph, children, project_context)

        return await self._run_leaf(session, agent, task, pack)

    async def _run_with_children(
        self,
        session: SessionState,
        agent: AgentState,
        task: Task,
        graph: TaskGraph,
        children: list[Task],
        project_context: str,
    ) -> dict[str, Any]:
        agent.status = AgentStatus.WAITING_CHILDREN
        child_agents = []
        for child_task in children:
            if not agent.can_spawn():
                break
            ca = self._spawn_agent(session, child_task, agent.depth + 1, agent.agent_id)
            agent.children.append(ca.agent_id)
            agent.budgets.children_spawned += 1
            agent.budgets.spawn_budget_remaining -= 1
            child_agents.append((ca, child_task))
            self._emit(
                session.session_id,
                EventType.CHILD_SPAWNED,
                agent.agent_id,
                task.task_id,
                f"spawned {ca.domain}",
                {"child_id": ca.agent_id},
            )

        async def run_one(ca: AgentState, ct: Task):
            return await self._execute_agent(session, ca, ct, graph, project_context)

        results = await asyncio.gather(
            *[run_one(ca, ct) for ca, ct in child_agents],
            return_exceptions=True,
        )

        summaries = []
        artifacts = []
        findings = []
        status = "success"
        for r in results:
            if isinstance(r, Exception):
                status = "partial"
                summaries.append(f"error: {r}")
                continue
            summaries.append(r.get("summary", ""))
            artifacts.extend(r.get("artifacts", []))
            findings.extend(r.get("findings", []))
            if r.get("status") == "failed":
                status = "partial"

        final = {
            "status": status,
            "summary": " | ".join(s for s in summaries if s)[:2000],
            "artifacts": artifacts,
            "findings": findings,
            "open_questions": [],
            "verification": {},
        }
        agent.status = AgentStatus.SUCCEEDED if status == "success" else AgentStatus.PARTIAL
        agent.result_summary = final["summary"]
        task.status = TaskStatus.SUCCEEDED if status == "success" else TaskStatus.PARTIAL
        task.result = final
        self._emit(session.session_id, EventType.COMPLETED, agent.agent_id, task.task_id, final["summary"][:200])
        return final

    async def _run_leaf(
        self,
        session: SessionState,
        agent: AgentState,
        task: Task,
        pack,
    ) -> dict[str, Any]:
        config = session.provider_config
        assert config is not None
        api_key = self.get_credential(config.credential_ref or config.provider)
        provider = self.providers.create(config, api_key)

        system = pack.to_prompt_block()
        messages = [
            Message(role="system", content=system),
            Message(
                role="user",
                content=(
                    f"Objective: {task.objective}\n\n"
                    "Return a concise result. If you need a tool, respond with a single JSON object:\n"
                    '{"tool":"<name>","input":{...}}\n'
                    "Otherwise respond with plain text summary of the work."
                ),
            ),
        ]

        tool_specs = [
            ToolSpec(name=t["name"], description=t["description"], parameters=t.get("parameters", {}))
            for t in pack.tool_contracts
        ]

        try:
            response = await provider.invoke(
                messages,
                model=config.model,
                tools=tool_specs if tool_specs else None,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        except Exception as e:
            agent.status = AgentStatus.FAILED
            agent.error = str(e)
            task.status = TaskStatus.FAILED
            self._emit(session.session_id, EventType.FAILED, agent.agent_id, task.task_id, str(e))
            return {"status": "failed", "summary": str(e), "artifacts": [], "findings": [], "open_questions": [], "verification": {}}

        agent.budgets.token_used += response.usage.get("total_tokens", 0)

        if response.tool_calls:
            tool_outputs = []
            for tc in response.tool_calls:
                name = tc.get("name")
                args = tc.get("arguments") or {}
                out = await self._invoke_tool(session, agent, name, args)
                tool_outputs.append(out)
            summary = "\n".join(o.output or o.error or "" for o in tool_outputs)[:3000]
            status = "success" if all(o.success for o in tool_outputs) else "partial"
        else:
            content = response.content or ""
            tool_call = self._parse_inline_tool(content)
            if tool_call:
                out = await self._invoke_tool(session, agent, tool_call["tool"], tool_call.get("input") or {})
                summary = out.output or out.error or ""
                status = "success" if out.success else "failed"
            else:
                summary = content[:3000]
                status = "success"

        final = {
            "status": status,
            "summary": summary,
            "artifacts": [],
            "findings": [],
            "open_questions": [],
            "verification": {},
        }
        agent.status = AgentStatus.SUCCEEDED if status == "success" else AgentStatus.PARTIAL
        agent.result_summary = summary
        task.status = TaskStatus.SUCCEEDED if status == "success" else TaskStatus.PARTIAL
        task.result = final
        self._emit(session.session_id, EventType.COMPLETED, agent.agent_id, task.task_id, summary[:200])
        return final

    def _parse_inline_tool(self, text: str) -> dict | None:
        text = text.strip()
        if not text.startswith("{"):
            return None
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "tool" in data:
                return data
        except json.JSONDecodeError:
            pass
        return None

    async def _invoke_tool(
        self,
        session: SessionState,
        agent: AgentState,
        tool_name: str,
        tool_input: dict,
    ) -> ToolResult:
        tool = self.tools.get(tool_name)
        if tool is None:
            return ToolResult(success=False, error=f"unknown tool: {tool_name}")

        req = self.permissions.request(
            session.session_id,
            agent.agent_id,
            tool_name,
            tool_input,
            risk=tool.risk,
        )
        self._emit(
            session.session_id,
            EventType.TOOL_PERMISSION_REQUESTED,
            agent.agent_id,
            agent.task_id,
            f"permission for {tool_name}",
            {"request_id": req.request_id, "tool": tool_name},
        )

        if req.decision == PermissionDecision.DENIED:
            return ToolResult(success=False, error="permission denied")

        if req.decision == PermissionDecision.PENDING:
            agent.status = AgentStatus.WAITING_PERMISSION
            for _ in range(120):
                await asyncio.sleep(0.5)
                if self._cancel_flags.get(session.session_id):
                    return ToolResult(success=False, error="cancelled")
                pending = self.permissions.get_pending(session.session_id)
                still = [p for p in pending if p.request_id == req.request_id]
                if not still:
                    break
            final_pending = [p for p in self.permissions.get_pending(session.session_id) if p.request_id == req.request_id]
            if final_pending and final_pending[0].decision == PermissionDecision.PENDING:
                self.permissions.decide(req.request_id, PermissionDecision.DENIED)
                return ToolResult(success=False, error="permission timed out")
            if final_pending and final_pending[0].decision == PermissionDecision.DENIED:
                return ToolResult(success=False, error="permission denied")

        self._emit(session.session_id, EventType.TOOL_STARTED, agent.agent_id, agent.task_id, tool_name)
        result = await tool.execute(tool_input, runtime=self)
        self._emit(
            session.session_id,
            EventType.TOOL_FINISHED,
            agent.agent_id,
            agent.task_id,
            tool_name,
            {"success": result.success},
        )
        agent.status = AgentStatus.RUNNING
        return result

    def cancel(self, session_id: str) -> None:
        self._cancel_flags[session_id] = True
        self.sessions.cancel(session_id)

    def get_agent_tree(self, session_id: str) -> list[dict]:
        agents = [a for a in self._agents.values() if a.session_id == session_id]
        return [
            {
                "agent_id": a.agent_id,
                "parent_id": a.parent_id,
                "domain": a.domain,
                "status": a.status.value,
                "objective": a.objective[:120],
                "depth": a.depth,
            }
            for a in agents
        ]
