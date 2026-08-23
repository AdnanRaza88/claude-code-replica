from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.models.context import ContextPack, ContextRef


DOMAIN_MAP: dict[str, list[str]] = {
    "orchestrator": ["System prompt", "Harness", "Communicating with the user", "Agents", "Task"],
    "planning": ["EnterPlanMode", "ExitPlanMode", "Task", "System prompt"],
    "research": ["Context management", "Harness"],
    "implementation": ["System prompt", "Harness"],
    "code-review": ["System prompt", "Harness"],
    "testing": ["System prompt", "Harness"],
    "git": ["Git"],
    "frontend": ["DesignSync", "Artifact"],
    "backend": ["System prompt", "Harness"],
    "security": ["System prompt", "Harness"],
    "docs": ["System prompt", "Harness"],
    "browser": ["Claude in Chrome browser automation"],
    "tools": ["Bash", "Read", "Write", "Edit", "WebSearch", "WebFetch"],
    "memory": ["Memory"],
    "general": ["System prompt", "Harness", "Communicating with the user"],
    "harness": ["Harness", "Communicating with the user", "Session-specific guidance", "Context management"],
    "agents": ["Agents", "Agent", "ListAgents", "SendMessage"],
    "design": ["DesignSync", "Artifact"],
    "scheduling": ["CronCreate", "CronDelete", "CronList", "ScheduleWakeup"],
}


class ContextIndexer:
    def __init__(self):
        self.headings: list[ContextRef] = []
        self._content_by_id: dict[str, str] = {}
        self._raw_lines: list[str] = []

    def index_file(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        self.index_text(text)

    def index_text(self, text: str) -> None:
        self._raw_lines = text.splitlines()
        heading_re = re.compile(r"^(#{1,3})\s+(.+)$")
        current: ContextRef | None = None
        buffer: list[str] = []

        def flush():
            nonlocal current, buffer
            if current is not None:
                body = "\n".join(buffer).strip()
                self._content_by_id[current.context_id] = body
                self.headings.append(current)
            buffer = []

        for i, line in enumerate(self._raw_lines, start=1):
            m = heading_re.match(line)
            if m:
                flush()
                level = len(m.group(1))
                title = m.group(2).strip()
                cid = f"h{i}-{re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()[:48]}"
                current = ContextRef(
                    context_id=cid,
                    heading=title,
                    start_line=i,
                    priority=level,
                )
            else:
                if current is not None:
                    buffer.append(line)
        flush()

    def find_by_heading(self, name: str) -> list[ContextRef]:
        name_l = name.lower()
        return [h for h in self.headings if name_l in h.heading.lower()]

    def get_content(self, context_id: str, max_chars: int = 4000) -> str:
        body = self._content_by_id.get(context_id, "")
        if len(body) > max_chars:
            return body[:max_chars] + "\n...[truncated]"
        return body


class ContextService:
    def __init__(self, skill_service=None):
        self.indexer = ContextIndexer()
        self._packs: dict[str, ContextPack] = {}
        self.skill_service = skill_service

    def load_source(self, path: str | Path) -> None:
        self.indexer.index_file(path)

    def set_skill_service(self, skill_service) -> None:
        self.skill_service = skill_service

    def build_pack(
        self,
        domain: str,
        project_context: str = "",
        skill_ids: list[str] | None = None,
        tool_contracts: list[dict[str, Any]] | None = None,
        role_instructions: str = "",
        max_excerpts: int = 6,
        max_chars_per_excerpt: int = 2500,
    ) -> ContextPack:
        heading_names = DOMAIN_MAP.get(domain, DOMAIN_MAP["general"])
        excerpts: list[str] = []
        refs: list[str] = []

        for name in heading_names:
            matches = self.indexer.find_by_heading(name)
            for ref in matches[:2]:
                body = self.indexer.get_content(ref.context_id, max_chars_per_excerpt)
                if body:
                    excerpts.append(f"### {ref.heading}\n{body}")
                    refs.append(ref.context_id)
                if len(excerpts) >= max_excerpts:
                    break
            if len(excerpts) >= max_excerpts:
                break

        skill_sections: list[str] = []
        resolved_skill_ids = list(skill_ids or [])
        if self.skill_service is not None:
            if not resolved_skill_ids:
                primary = self.skill_service.primary_for_domain(domain)
                if primary:
                    resolved_skill_ids = [primary.skill_id]
            for sid in resolved_skill_ids:
                skill = self.skill_service.get(sid)
                if skill:
                    skill_sections.append(skill.to_prompt_section())

        role = role_instructions or self._default_role(domain)
        if skill_sections and not role_instructions:
            role = self._short_role(domain)

        pack = ContextPack(
            domain=domain,
            role_instructions=role,
            source_excerpts=excerpts,
            project_context=project_context,
            skill_ids=resolved_skill_ids,
            tool_contracts=tool_contracts or [],
            token_estimate=(
                sum(len(e) // 4 for e in excerpts)
                + sum(len(s) // 4 for s in skill_sections)
                + len(project_context) // 4
            ),
            metadata={
                "context_refs": refs,
                "skill_sections": skill_sections,
            },
        )
        self._packs[pack.pack_id] = pack
        return pack

    def _short_role(self, domain: str) -> str:
        roles = {
            "orchestrator": "You are the main orchestrator. Decompose, spawn specialists, synthesize. Do not do deep implementation yourself.",
            "planning": "You are the planning agent. Produce a clear task decomposition.",
            "research": "You are the research agent. Explore and summarize accurately. Do not modify code.",
            "implementation": "You are the implementation agent. Write clean, minimal, production-quality code.",
            "code-review": "You are the code-review agent. Be strict, specific, and severity-ordered.",
            "testing": "You are the testing agent. Write and run meaningful tests.",
            "git": "You are the git agent. Inspect first, mutate only with permission, keep commits focused.",
            "frontend": "You are the frontend agent. Match design system, accessibility, and existing patterns.",
            "backend": "You are the backend agent. Validate input, keep handlers thin, stable contracts.",
            "security": "You are the security agent. Find and report risks; do not silently fix critical issues.",
            "docs": "You are the documentation agent. Short, accurate, example-driven docs.",
            "browser": "You are the browser agent. Short deterministic actions, no loops.",
            "tools": "You are the tools/shell agent. Prefer safe commands; summarize output.",
            "memory": "You are the memory agent. Store only durable high-value facts.",
            "general": "You are a software engineering agent. Prefer concrete action over speculation.",
        }
        return roles.get(domain, roles["general"])

    def _default_role(self, domain: str) -> str:
        return self._short_role(domain)

    def get_pack(self, pack_id: str) -> ContextPack | None:
        return self._packs.get(pack_id)
