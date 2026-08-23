from __future__ import annotations

import re
from src.models.task import Task, TaskGraph


DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "git": ["git", "commit", "branch", "pull request", "pr ", "merge", "diff", "repo"],
    "browser": ["browser", "chrome", "navigate", "webpage", "screenshot"],
    "design": ["ui", "frontend", "css", "component", "layout", "design", "responsive"],
    "planning": ["plan", "architecture", "design the system", "decompose"],
    "memory": ["remember", "memory", "persist"],
    "tools": ["run command", "bash", "shell", "execute"],
    "scheduling": ["schedule", "cron", "later", "recurring"],
}


class Planner:
    def __init__(self):
        pass

    def detect_domains(self, objective: str) -> list[str]:
        text = objective.lower()
        found = []
        for domain, kws in DOMAIN_KEYWORDS.items():
            if any(k in text for k in kws):
                found.append(domain)
        if not found:
            found.append("general")
        return found

    def create_graph(self, session_id: str, objective: str) -> TaskGraph:
        graph = TaskGraph(session_id=session_id)
        domains = self.detect_domains(objective)

        root = Task(
            objective=objective,
            domain="planning" if len(domains) > 1 else domains[0],
            expected_output="structured result with summary and artifacts",
            verification_strategy="basic",
        )
        graph.add_task(root)

        if len(domains) > 1 or self._should_split(objective):
            for domain in domains:
                child = Task(
                    objective=f"[{domain}] {objective}",
                    domain=domain,
                    parent_task_id=root.task_id,
                    expected_output="domain result",
                )
                graph.add_task(child)
                graph.add_dependency(root.task_id, child.task_id)

        return graph

    def _should_split(self, objective: str) -> bool:
        words = objective.split()
        if len(words) > 40:
            return True
        if re.search(r"\band\b.+\band\b", objective.lower()):
            return True
        return False

    def expand_task(self, parent: Task, sub_objectives: list[str]) -> list[Task]:
        children = []
        for obj in sub_objectives:
            t = Task(
                objective=obj,
                domain=parent.domain,
                parent_task_id=parent.task_id,
                required_tools=parent.required_tools[:],
                required_skills=parent.required_skills[:],
            )
            children.append(t)
        return children
