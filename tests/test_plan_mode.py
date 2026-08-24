from src.services.session_service import SessionService
from src.orchestration.runtime import (
    PLAN_MODE_ALLOWED_TOOLS,
    PLAN_MODE_BLOCKED_TOOLS,
    AgentRuntime,
)
from src.models.provider import ProviderConfig
from src.models.task import Task
from src.services.permission_service import PermissionService
from src.services.event_service import EventService
from src.services.context_service import ContextService
from src.adapters.providers.registry import ProviderRegistry
from src.tools.base import ToolRegistry, Tool, ToolResult


class _StubTool(Tool):
    def __init__(self, name: str, risk: str = "medium"):
        self.name = name
        self.description = name
        self.risk = risk

    async def execute(self, input_data, runtime=None):
        return ToolResult(success=True, output=f"ran {self.name}")


def _runtime_with_tools():
    tools = ToolRegistry()
    for n, r in [
        ("read", "low"),
        ("search", "low"),
        ("web_search", "low"),
        ("web_fetch", "low"),
        ("github", "low"),
        ("write", "high"),
        ("edit", "high"),
        ("bash", "high"),
    ]:
        tools.register(_StubTool(n, r))
    sessions = SessionService()
    return AgentRuntime(
        session_service=sessions,
        permission_service=PermissionService(),
        event_service=EventService(),
        context_service=ContextService(),
        provider_registry=ProviderRegistry(),
        tool_registry=tools,
        use_harness=False,
    ), sessions


def test_session_mode_defaults_agent():
    s = SessionService()
    sess = s.create()
    assert sess.mode == "agent"


def test_session_set_mode_and_last_plan():
    s = SessionService()
    sess = s.create(mode="plan")
    assert sess.mode == "plan"
    s.set_mode(sess.session_id, "agent")
    assert s.get(sess.session_id).mode == "agent"
    s.set_last_plan(sess.session_id, {"summary": "plan text"})
    assert s.get_last_plan(sess.session_id)["summary"] == "plan text"


def test_filter_tools_plan_mode():
    rt, sessions = _runtime_with_tools()
    sess = sessions.create(mode="plan")
    filtered = rt._filter_tools_for_mode(sess, ["read", "write", "bash", "web_search", "github", "pinchtab"])
    assert set(filtered) == {"read", "web_search", "github"}
    assert "write" not in filtered
    assert "bash" not in filtered


def test_filter_tools_agent_mode_unchanged():
    rt, sessions = _runtime_with_tools()
    sess = sessions.create(mode="agent")
    raw = ["read", "write", "bash", "web_search"]
    assert rt._filter_tools_for_mode(sess, raw) == raw


def test_invoke_blocks_write_in_plan_mode():
    import asyncio
    from src.models.agent import AgentState, AgentStatus, BudgetState

    rt, sessions = _runtime_with_tools()
    sess = sessions.create(
        mode="plan",
        provider_config=ProviderConfig(provider="ollama", model="x"),
    )
    agent = AgentState(
        task_id="t1",
        session_id=sess.session_id,
        domain="general",
        role="worker",
        objective="test",
        allowed_tools=list(PLAN_MODE_ALLOWED_TOOLS),
        status=AgentStatus.RUNNING,
        budgets=BudgetState(),
    )
    out = asyncio.run(rt._invoke_tool(sess, agent, "write", {"path": "x.py", "content": "hi"}))
    assert out.success is False
    assert "blocked in plan mode" in (out.error or "")
    assert "write" in (out.error or "")


def test_invoke_allows_read_in_plan_mode():
    import asyncio
    from src.models.agent import AgentState, AgentStatus, BudgetState

    rt, sessions = _runtime_with_tools()
    sess = sessions.create(
        mode="plan",
        provider_config=ProviderConfig(provider="ollama", model="x"),
    )
    agent = AgentState(
        task_id="t1",
        session_id=sess.session_id,
        domain="general",
        role="worker",
        objective="test",
        allowed_tools=list(PLAN_MODE_ALLOWED_TOOLS),
        status=AgentStatus.RUNNING,
        budgets=BudgetState(),
    )
    out = asyncio.run(rt._invoke_tool(sess, agent, "read", {"path": "x.py"}))
    assert out.success is True


def test_allowed_blocked_sets():
    assert PLAN_MODE_BLOCKED_TOOLS.isdisjoint(PLAN_MODE_ALLOWED_TOOLS)
    for t in ("write", "edit", "bash"):
        assert t in PLAN_MODE_BLOCKED_TOOLS
    for t in ("read", "search", "web_search", "web_fetch", "github"):
        assert t in PLAN_MODE_ALLOWED_TOOLS
