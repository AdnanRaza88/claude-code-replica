from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from src.adapters.providers.registry import ProviderRegistry
from src.models.permission import PermissionMode
from src.models.provider import ProviderConfig
from src.orchestration.runtime import AgentRuntime
from src.services.context_service import ContextService
from src.services.event_service import EventService
from src.services.permission_service import PermissionService
from src.services.session_service import SessionService, SessionState
from src.services.skill_service import SkillService
from src.tools.agent_reach_tool import AgentReachTool
from src.tools.base import ToolRegistry
from src.tools.bash_tool import BashTool
from src.tools.file_tools import EditTool, ReadTool, WriteTool
from src.tools.github_tool import GitHubTool
from src.tools.memory_tool import MemoryTool
from src.tools.pinchtab_tool import PinchTabTool
from src.tools.search_tools import ProjectSearchTool
from src.tools.web_tools import WebFetchTool, WebSearchTool
from src.tools.code_graph_tool import CodeGraphTool
from src.tools.text_tools import DefuddleTool, HumanizeTool

ROOT = Path(__file__).resolve().parents[1]


class Engine:
    def __init__(self, workspace: Optional[Path] = None) -> None:
        self.root = workspace or ROOT
        persist = self.root / ".agentforge" / "sessions"
        self.sessions = SessionService(persist_dir=persist)
        self.permissions = PermissionService(default_mode=PermissionMode.SESSION_ALLOW)
        self.events = EventService()
        self.providers = ProviderRegistry()
        self.tools = ToolRegistry()
        self.credentials: dict[str, dict[str, Optional[str]]] = {}

        skills = None
        skills_root = self.root / "skills"
        if skills_root.exists():
            skills = SkillService(skills_root)
            skills.load_all()
        self.skills = skills

        try:
            ctx = ContextService(skill_service=skills)
        except TypeError:
            ctx = ContextService()
            if skills is not None and hasattr(ctx, "set_skill_service"):
                ctx.set_skill_service(skills)
        self.context = ctx

        source = self.root / "knowledge" / "source_headings.md"
        if source.exists():
            ctx.load_source(source)
        knowledge_dir = self.root / "knowledge" / "claude_code"
        if knowledge_dir.exists() and hasattr(ctx, "load_knowledge_dir"):
            ctx.load_knowledge_dir(knowledge_dir)

        self._register_tools()

        self.runtime = AgentRuntime(
            self.sessions,
            self.permissions,
            self.events,
            self.context,
            self.providers,
            self.tools,
            get_credential=self._get_credential,
            skill_service=self.skills,
        )

    def _register_tools(self) -> None:
        root = self.root
        self.tools.register(ReadTool(root))
        self.tools.register(WriteTool(root))
        self.tools.register(EditTool(root))
        self.tools.register(ProjectSearchTool(root))
        self.tools.register(BashTool(root))
        self.tools.register(GitHubTool(get_token=lambda: self._lookup_cred("github")))
        self.tools.register(WebSearchTool())
        self.tools.register(WebFetchTool())
        self.tools.register(
            PinchTabTool(
                get_base_url=lambda: self._lookup_cred("pinchtab_url") or "http://127.0.0.1:9867",
                get_token=lambda: self._lookup_cred("pinchtab_token"),
            )
        )
        self.tools.register(AgentReachTool())
        self.tools.register(MemoryTool(project_root=str(root)))
        self.tools.register(CodeGraphTool(root))
        self.tools.register(DefuddleTool())
        self.tools.register(HumanizeTool())

    def _lookup_cred(self, name: str) -> Optional[str]:
        for bag in self.credentials.values():
            val = bag.get(name)
            if val:
                return val
        return os.environ.get(name.upper()) or os.environ.get(f"{name.upper()}_TOKEN")

    def _get_credential(self, ref: Optional[str]) -> Optional[str]:
        if not ref:
            return None
        for bag in self.credentials.values():
            if bag.get(ref):
                return bag[ref]
        return os.environ.get(ref) or os.environ.get(ref.upper())

    def create_session(
        self,
        provider: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        workspace: Optional[str] = None,
        mode: str = "agent",
        permission_mode: str = "session_allow",
    ) -> SessionState:
        chosen_model = model or self.providers.default_model(provider) or "default"
        cfg = ProviderConfig(
            provider=provider,
            model=chosen_model,
            base_url=base_url or self.providers.default_base_url(provider) or None,
            credential_ref="api_key" if api_key else None,
        )
        try:
            perm = PermissionMode(permission_mode)
        except ValueError:
            perm = PermissionMode.SESSION_ALLOW
        session = self.sessions.create(
            provider_config=cfg,
            permission_mode=perm,
            project_root=workspace or str(self.root),
            mode=mode if mode in ("agent", "plan") else "agent",
        )
        self.permissions.set_session_mode(session.session_id, perm)
        bag: dict[str, Optional[str]] = {}
        if api_key:
            bag["api_key"] = api_key
        self.credentials[session.session_id] = bag
        return session

    def get_session(self, session_id: str) -> SessionState | None:
        return self.sessions.get(session_id)

    def list_sessions(self) -> list[SessionState]:
        return self.sessions.list_sessions()

    def list_tools(self) -> list[dict[str, Any]]:
        return self.tools.specs_for()

    def list_skills(self) -> list[dict[str, Any]]:
        if self.skills is None:
            return []
        out = []
        for skill_id in self.skills.list_ids():
            skill = self.skills.get(skill_id)
            if skill is None:
                continue
            out.append(
                {
                    "id": skill.skill_id,
                    "name": skill.name,
                    "domain": skill.domain,
                    "description": skill.description,
                    "allowed_tools": skill.allowed_tools,
                    "priority": skill.priority,
                    "version": skill.version,
                }
            )
        return sorted(out, key=lambda s: (s["domain"], s["name"]))

    def get_skill(self, skill_id: str) -> dict[str, Any] | None:
        if self.skills is None:
            return None
        skill = self.skills.get(skill_id)
        if skill is None:
            for candidate in self.skills.list_ids():
                if candidate.endswith("/" + skill_id) or candidate == skill_id:
                    skill = self.skills.get(candidate)
                    break
        if skill is None:
            return None
        return {
            "id": skill.skill_id,
            "name": skill.name,
            "domain": skill.domain,
            "description": skill.description,
            "allowed_tools": skill.allowed_tools,
            "priority": skill.priority,
            "version": skill.version,
            "body": skill.body,
        }

    async def run(self, session_id: str, objective: str, plan_only: bool = False) -> dict[str, Any]:
        session = self.sessions.get(session_id)
        if session is None:
            raise KeyError("session not found")
        if plan_only:
            self.sessions.set_mode(session_id, "plan")
        else:
            self.sessions.set_mode(session_id, session.mode or "agent")
        return await self.runtime.run_task(session_id, objective)

    def session_graph(self, session_id: str) -> dict[str, Any]:
        graph = self.runtime._graphs.get(session_id)
        agents = [a for a in self.runtime._agents.values() if a.session_id == session_id]
        nodes = []
        if graph is not None:
            for task in graph.tasks.values():
                assigned = next((a for a in agents if a.agent_id == task.assigned_agent_id), None)
                parent = None
                if assigned and assigned.parent_id:
                    parent = assigned.parent_id
                elif task.parent_task_id:
                    parent = task.parent_task_id
                status = (
                    assigned.status.value
                    if assigned is not None and hasattr(assigned.status, "value")
                    else (task.status.value if hasattr(task.status, "value") else str(task.status))
                )
                nodes.append(
                    {
                        "id": (assigned.agent_id if assigned else task.task_id),
                        "task_id": task.task_id,
                        "parent_id": parent,
                        "domain": (assigned.domain if assigned else task.domain),
                        "role": (assigned.role if assigned else "worker"),
                        "status": status,
                        "objective": task.objective,
                    }
                )
        elif agents:
            for assigned in agents:
                nodes.append(
                    {
                        "id": assigned.agent_id,
                        "task_id": assigned.task_id,
                        "parent_id": assigned.parent_id,
                        "domain": assigned.domain,
                        "role": assigned.role,
                        "status": assigned.status.value if hasattr(assigned.status, "value") else str(assigned.status),
                        "objective": assigned.objective,
                    }
                )
        pending = self.permissions.get_pending(session_id)
        return {
            "session_id": session_id,
            "root_task_id": graph.root_task_id if graph else None,
            "nodes": nodes,
            "pending_permissions": [self._perm_out(p) for p in pending],
        }

    def pending_permissions(self, session_id: str) -> list[dict[str, Any]]:
        return [self._perm_out(p) for p in self.permissions.get_pending(session_id)]

    def decide_permission(self, session_id: str, request_id: str, decision: str) -> dict[str, Any] | None:
        from src.models.permission import PermissionDecision

        if decision not in ("approved", "denied"):
            raise ValueError("decision must be approved or denied")
        req = self.permissions.get_pending(session_id)
        match = next((r for r in req if r.request_id == request_id), None)
        if match is None:
            existing = self.permissions.get_decision(request_id)
            if existing is None or existing.session_id != session_id:
                return None
            return self._perm_out(existing)
        decided = self.permissions.decide(request_id, PermissionDecision(decision))
        if decided is None:
            return None
        return self._perm_out(decided)

    def _perm_out(self, req) -> dict[str, Any]:
        return {
            "request_id": req.request_id,
            "session_id": req.session_id,
            "agent_id": req.agent_id,
            "tool_name": req.tool_name,
            "risk": req.risk,
            "reason": req.reason,
            "decision": req.decision.value if hasattr(req.decision, "value") else str(req.decision),
            "created_at": req.created_at.isoformat() if req.created_at else None,
        }

    def session_events(self, session_id: str, after: int = 0) -> list[dict[str, Any]]:
        events = self.events.list_events(session_id, limit=2000)
        sliced = events[after:]
        out = []
        for i, ev in enumerate(sliced, start=after):
            out.append(
                {
                    "index": i,
                    "event_id": ev.event_id,
                    "type": ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type),
                    "message": ev.message,
                    "agent_id": ev.agent_id,
                    "task_id": ev.task_id,
                    "parent_agent_id": ev.parent_agent_id,
                    "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                    "payload": ev.payload,
                }
            )
        return out


_ENGINE: Engine | None = None


def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = Engine()
    return _ENGINE
