from __future__ import annotations

import re
from src.models.task import Task, TaskGraph


DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "orchestrator": ["orchestrate", "coordinate agents", "multi agent", "kitne agents", "how many agents"],
    "research": [
        "explore", "research", "find where", "locate", "investigate", "how does", "search codebase",
        "internet", "web search", "browse", "news", "latest news", "current events", "aaj ki date",
        "today's date", "google news", "search the web", "online", "what is happening",
        "latest update", "latest updates", "headlines", "fetch from web", "look up",
        "youtube", "reddit", "twitter", "transcript", "agent reach", "agent_reach", "wikipedia",
    ],
    "implementation": ["implement", "add feature", "write code", "build", "create function", "fix bug", "refactor"],
    "code-review": ["review", "code review", "pr review", "critique", "audit code"],
    "testing": ["unit test", "pytest", "test coverage", "tdd", "write tests", "run tests"],
    "git": [
        "git ", "commit", "branch", "pull request", "pr ", "merge", "diff", "repo", "repos",
        "push", "github", "profile", "bio", "repositories", "my repos", "meri repos",
        "github token", "github account",
    ],
    "frontend": ["ui", "frontend", "css", "component", "layout", "react", "vue", "html", "responsive", "design system"],
    "backend": ["backend", "api", "endpoint", "server", "route", "service layer", "handler"],
    "security": ["security", "auth", "vulnerability", "xss", "sql injection", "secret", "cve", "permission"],
    "docs": ["document", "readme", "docs", "changelog", "architecture note"],
    "browser": [
        "browser", "chrome", "navigate", "webpage", "screenshot", "playwright", "selenium",
        "pinchtab", "click", "open site", "open url", "visit page", "fill form", "scrape page",
    ],
    "tools": ["run command", "bash", "shell", "execute", "terminal"],
    "memory": ["remember", "memory", "persist fact", "forget"],
    "planning": [
        "plan", "architecture", "design the system", "decompose", "roadmap",
        "spec", "prd", "trd", "sdd", "spec driven", "spec-driven", "acceptance criteria",
        "write a prd", "product requirements", "task waves", "project bible",
    ],
}

_WORD_BOUNDARY_KEYWORDS: dict[str, list[str]] = {
    "testing": ["test", "tests", "spec", "specs"],
    "git": ["git"],
}

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
    "planning": "sdd/sdd",
    "general": "general/general",
}

DOMAIN_TOOLS: dict[str, list[str]] = {
    "orchestrator": ["read", "search", "github", "web_search", "web_fetch", "pinchtab", "agent_reach", "memory"],
    "research": ["web_search", "web_fetch", "read", "search", "bash", "github", "pinchtab", "agent_reach", "memory"],
    "implementation": ["read", "write", "edit", "search", "bash", "web_search", "memory"],
    "code-review": ["read", "search", "github", "web_search", "web_fetch", "memory"],
    "testing": ["read", "write", "edit", "search", "bash", "web_search", "memory"],
    "git": ["bash", "read", "search", "github", "web_search", "memory"],
    "frontend": ["read", "write", "edit", "search", "bash", "web_search", "memory"],
    "backend": ["read", "write", "edit", "search", "bash", "web_search", "memory"],
    "security": ["read", "search", "bash", "web_search", "memory"],
    "docs": ["read", "write", "edit", "search", "web_search", "web_fetch", "agent_reach", "memory"],
    "browser": ["web_search", "web_fetch", "pinchtab", "agent_reach", "bash", "read", "search", "memory"],
    "tools": ["bash", "read", "search", "web_search", "memory"],
    "memory": ["memory", "read", "search"],
    "planning": ["read", "search", "web_search", "write", "edit", "memory"],
    "general": ["web_search", "web_fetch", "read", "write", "edit", "search", "bash", "github", "pinchtab", "agent_reach", "memory"],
}

IMPLEMENTATION_DOMAINS = frozenset(
    {"implementation", "frontend", "backend", "testing"}
)


class Planner:
    def __init__(self, skill_service=None, strict_sdd: bool = True):
        self.skill_service = skill_service
        self.strict_sdd = strict_sdd

    def detect_domains(self, objective: str) -> list[str]:
        text = objective.lower()
        found: list[str] = []
        for domain, kws in DOMAIN_KEYWORDS.items():
            if any(k in text for k in kws):
                found.append(domain)
        for domain, words in _WORD_BOUNDARY_KEYWORDS.items():
            for w in words:
                if re.search(rf"(?<![a-z0-9]){re.escape(w)}(?![a-z0-9])", text):
                    if domain not in found:
                        found.append(domain)
                    break
        if not found:
            found.append("general")
        research_signals = (
            "internet", "news", "browse", "web search", "online", "latest update",
            "aaj ki date", "today", "google", "headlines", "current", "wikipedia",
        )
        if any(s in text for s in research_signals) and "research" not in found:
            found.insert(0, "research")
        elif any(s in text for s in research_signals) and "research" in found:
            found = ["research"] + [d for d in found if d != "research"]
        seen = set()
        ordered = []
        for d in found:
            if d not in seen:
                seen.add(d)
                ordered.append(d)
        return ordered

    def is_spec_request(self, objective: str) -> bool:
        text = objective.lower()
        signals = (
            "write a prd", "prd-lite", "trd-lite", "spec driven", "spec-driven",
            "create specs", "spec pipeline", "acceptance criteria", "project bible",
            "task waves", "plan mode", "produce a plan", "design the system",
        )
        return any(s in text for s in signals)

    def is_build_request(self, objective: str) -> bool:
        text = objective.lower()
        if self.is_spec_request(objective):
            return False
        build = ("implement", "build", "add feature", "write code", "create app", "ship")
        return any(b in text for b in build)

    def _skill_for(self, domain: str) -> list[str]:
        sid = DOMAIN_PRIMARY_SKILL.get(domain)
        if domain == "planning":
            return ["sdd/sdd", "planning/planning"]
        if sid:
            return [sid]
        return []

    def _tools_for(self, domain: str) -> list[str]:
        return list(DOMAIN_TOOLS.get(domain, DOMAIN_TOOLS["general"]))

    def create_graph(
        self,
        session_id: str,
        objective: str,
        *,
        mode: str = "agent",
        specs_locked: bool = False,
    ) -> TaskGraph:
        graph = TaskGraph(session_id=session_id)
        domains = self.detect_domains(objective)

        if mode == "plan" or self.is_spec_request(objective):
            return self._spec_graph(graph, objective)

        if (
            self.strict_sdd
            and self.is_build_request(objective)
            and not specs_locked
            and any(d in IMPLEMENTATION_DOMAINS for d in domains)
        ):
            return self._spec_graph(
                graph,
                objective,
                note="SDD gate: specs/bible not locked — produce Intent/PRD/TRD/WAVES/BIBLE first",
            )

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

    def _spec_graph(self, graph: TaskGraph, objective: str, note: str = "") -> TaskGraph:
        obj = objective
        if note:
            obj = f"{objective}\n\n[{note}]"
        root = Task(
            objective=obj,
            domain="planning",
            expected_output=(
                "Intent, PRD-lite, TRD-lite, task waves, bible under .agentforge/specs/; "
                "open questions; do not implement features yet"
            ),
            verification_strategy="specs_present",
            required_skills=self._skill_for("planning"),
            required_tools=self._tools_for("planning"),
        )
        graph.add_task(root)
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
