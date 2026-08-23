from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.models.context import ContextPack, ContextRef


DOMAIN_MAP: dict[str, list[str]] = {
    "harness": ["Harness", "Communicating with the user", "Session-specific guidance", "Context management"],
    "memory": ["Memory"],
    "planning": ["EnterPlanMode", "ExitPlanMode", "Task"],
    "agents": ["Agents", "Agent", "ListAgents", "SendMessage"],
    "tools": ["Bash", "Read", "Write", "Edit", "WebSearch", "WebFetch"],
    "git": ["Git"],
    "browser": ["Claude in Chrome browser automation"],
    "design": ["DesignSync", "Artifact"],
    "scheduling": ["CronCreate", "CronDelete", "CronList", "ScheduleWakeup"],
    "general": ["System prompt", "Harness", "Communicating with the user"],
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
    def __init__(self):
        self.indexer = ContextIndexer()
        self._packs: dict[str, ContextPack] = {}

    def load_source(self, path: str | Path) -> None:
        self.indexer.index_file(path)

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

        pack = ContextPack(
            domain=domain,
            role_instructions=role_instructions or self._default_role(domain),
            source_excerpts=excerpts,
            project_context=project_context,
            skill_ids=skill_ids or [],
            tool_contracts=tool_contracts or [],
            token_estimate=sum(len(e) // 4 for e in excerpts) + len(project_context) // 4,
            metadata={"context_refs": refs},
        )
        self._packs[pack.pack_id] = pack
        return pack

    def _default_role(self, domain: str) -> str:
        roles = {
            "planning": "You are the planning agent. Decompose the objective into clear typed tasks.",
            "agents": "You coordinate specialist agents and aggregate their results.",
            "tools": "You execute tools carefully and respect permission decisions.",
            "git": "You handle repository inspection and git operations under permission gates.",
            "memory": "You manage persistent memory facts and retrieval.",
            "browser": "You perform browser automation tasks with focus and without loops.",
            "design": "You produce design and frontend oriented outputs.",
            "scheduling": "You manage scheduled and one-shot background tasks.",
            "harness": "You enforce harness rules, communication style and context discipline.",
            "general": "You are a software engineering agent. Prefer concrete action over speculation.",
        }
        return roles.get(domain, roles["general"])

    def get_pack(self, pack_id: str) -> ContextPack | None:
        return self._packs.get(pack_id)
