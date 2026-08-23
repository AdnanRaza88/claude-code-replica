from src.models.agent import AgentState, BudgetState
from src.models.task import Task, TaskGraph, TaskStatus
from src.models.permission import PermissionMode, PermissionRequest


def test_agent_can_spawn():
    agent = AgentState(task_id="t1", session_id="s1", objective="test")
    assert agent.can_spawn() is True
    agent.budgets.max_depth = 0
    assert agent.can_spawn() is False


def test_task_graph_ready():
    graph = TaskGraph(session_id="s1")
    a = Task(objective="a")
    b = Task(objective="b")
    graph.add_task(a)
    graph.add_task(b)
    graph.add_dependency(a.task_id, b.task_id)
    ready = graph.ready_tasks()
    assert len(ready) == 1
    assert ready[0].task_id == a.task_id
    graph.mark(a.task_id, TaskStatus.SUCCEEDED)
    ready2 = graph.ready_tasks()
    assert any(t.task_id == b.task_id for t in ready2)


def test_permission_request():
    req = PermissionRequest(
        session_id="s1",
        agent_id="a1",
        tool_name="bash",
        tool_input={"command": "ls"},
    )
    assert req.decision.value == "pending"
