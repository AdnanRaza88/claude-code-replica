from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    objective: str
    domain: str = "general"
    dependencies: list[str] = Field(default_factory=list)
    context_scope: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    expected_output: str | None = None
    verification_strategy: str = "basic"
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent_id: str | None = None
    result: dict[str, Any] | None = None
    parent_task_id: str | None = None
    priority: int = 0


class TaskGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    root_task_id: str | None = None
    tasks: dict[str, Task] = Field(default_factory=dict)
    edges: list[tuple[str, str]] = Field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks[task.task_id] = task
        if self.root_task_id is None:
            self.root_task_id = task.task_id

    def add_dependency(self, upstream_id: str, downstream_id: str) -> None:
        if upstream_id not in self.tasks or downstream_id not in self.tasks:
            raise ValueError("unknown task id")
        edge = (upstream_id, downstream_id)
        if edge not in self.edges:
            self.edges.append(edge)
        if upstream_id not in self.tasks[downstream_id].dependencies:
            self.tasks[downstream_id].dependencies.append(upstream_id)

    def ready_tasks(self) -> list[Task]:
        ready = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            deps_done = all(
                self.tasks[d].status in {TaskStatus.SUCCEEDED, TaskStatus.PARTIAL}
                for d in task.dependencies
                if d in self.tasks
            )
            if deps_done:
                ready.append(task)
        return ready

    def mark(self, task_id: str, status: TaskStatus) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].status = status
