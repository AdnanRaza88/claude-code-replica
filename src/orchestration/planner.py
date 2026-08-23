from __future__ import annotations

import re
from src.models.task import Task, TaskGraph


# Domain → keywords for lightweight detection (LLM planner can replace later)
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "orchestrator": ["orchestrate", "coordinate agents", "multi agent", "kitne agents", "how many agents"],
    "research": ["explore", "research", "find where", "locate", "investigate", "how does", "search codebase"],
    "implementation": ["implement", "add feature", "write code", "build", "create function", "fix bug", "refactor"],
    "code-review": ["review", "code review", "pr review", "critique", "audit code"],
    "testing": ["test", "unit test", "pytest", "coverage", "spec", "tdd"],
    "git": [
        "git", "commit", "branch", "pull request", "pr ", "merge", "diff", "repo", "repos",
        "push", "github", "profile", "bio", "repositories", "my repos", "meri repos",
        "github token", "github account",
    ],
    "frontend": ["ui", "frontend", "css", "component", "layout", "react", "vue", "html", "responsive", "design system"],
    "backend": ["backend", "api", "endpoint", "server", "route", "service layer", "handler"],
    "security": ["security", "auth", "vulnerability", "xss", "sql injection", "secret", "cve", "permission"],
    "docs": ["document", "readme", "docs", "changelog", "architecture note"],
    "browser": ["browser", "chrome", "navigate", "webpage", "screenshot", "playwright", "selenium"],
    "tools": ["run command", "bash", "shell", "execute", "terminal"],
    "memory": ["remember", "memory", "persist fact", "forget"],
    "planning": ["plan", "architecture", "design the system", "decompose", "roadmap"],
}

# Primary skill id per domain (matches skills/<domain>/SKILL.md)
DOMAIN_PRIMARY_SKILL: dict[str, str] = {
    "orchestrator": "orchestrator/orchestrator",
    "research": "research/research",
    "implementation": "implementation/implementation",
    "code-review": "code-review/code-review",
    "testing": "testing/testing",
    "git": "git/git",
    "frontend": "frontend/frontend",
    "backend": "backend/backend",
    "security": "security/security",
    "docs": "docs/docs",
    "browser": "browser/browser",
    "tools": "tools/tools",
    "memory": "memory/memory",
    "planning": "orchestrator/orchestrator",
    "general": "general/general",
}

# Default tool allowlist per domain (permission service still gates)
DOMAIN_TOOLS: dict[str, list[str]] = {
    "orchestrator": ["read", "search", "github"],
    "research": ["read", "search", "bash", "github"],
    "implementation": ["read", "write", "edit", "search", "bash"],
    "code-review": ["read", "search", "github"],
    "testing": ["read", "write", "edit", "search", "bash"],
    "git": ["bash", "read", "search", "github"],
    "frontend": ["read", "write", "edit", "search", "bash"],
    "backend": ["read", "write", "edit", "search", "bash"],
    "security": ["read", "search", "bash"],
    "docs": ["read", "write", "edit", "search"],
    "browser": ["bash", "read", "search"],
    "tools": ["bash", "read", "search"],
    "memory": ["read", "write", "edit", "search"],
    "planning": ["read", "search"],
    "general": ["read", "write", "edit", "search", "bash", "github"],
}


class Planner:
    def __init__(self, skill_service=None):
        self.skill_service = skill_service

    def detect_domains(self, objective: str) -> list[str]:
        text = objective.lower()
        found: list[str] = []
        for domain, kws in DOMAIN_KEYWORDS.items():
            if any(k in text for k in kws):
                found.append(domain)
        if not found:
            found.append("general")
        # de-dupe preserve order
        seen = set()
        ordered = []
        for d in found:
            if d not in seen:
                seen.add(d)
                ordered.append(d)
        return ordered

    def _skill_for(self, domain: str) -> list[str]:
        sid = DOMAIN_PRIMARY_SKILL.get(domain)
        if sid:
            return [sid]
        return []

    def _tools_for(self, domain: str) -> list[str]:
        return list(DOMAIN_TOOLS.get(domain, DOMAIN_TOOLS["general"]))

    def create_graph(self, session_id: str, objective: str) -> TaskGraph:
        graph = TaskGraph(session_id=session_id)
        domains = self.detect_domains(objective)

        # Root is always orchestrator/planning when multi-domain or complex
        root_domain = "orchestrator" if (len(domains) > 1 or self._should_split(objective)) else domains[0]
        root = Task(
            objective=objective,
            domain=root_domain,
            expected_output="structured result with summary and artifacts",
            verification_strategy="basic",
            required_skills=self._skill_for(root_domain),
            required_tools=self._tools_for(root_domain),
        )
        graph.add_task(root)

        if root_domain == "orchestrator" or len(domains) > 1 or self._should_split(objective):
            child_domains = [d for d in domains if d not in ("orchestrator", "planning")]
            if not child_domains:
                child_domains = domains
            for domain in child_domains:
                child = Task(
                    objective=f"[{domain}] {objective}",
                    domain=domain,
                    parent_task_id=root.task_id,
                    expected_output="domain result",
                    required_skills=self._skill_for(domain),
                    required_tools=self._tools_for(domain),
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
            domain = parent.domain
            t = Task(
                objective=obj,
                domain=domain,
                parent_task_id=parent.task_id,
                required_tools=parent.required_tools[:] or self._tools_for(domain),
                required_skills=parent.required_skills[:] or self._skill_for(domain),
            )
            children.append(t)
        return children
