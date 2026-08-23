from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.models.skill import Skill


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    m = FRONTMATTER_RE.match(raw)
    if not m:
        return {}, raw
    meta: dict[str, Any] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip().strip('"').strip("'")
        if key in {"allowed_tools", "tools"} and val:
            meta["allowed_tools"] = [t.strip() for t in val.split(",") if t.strip()]
        else:
            meta[key] = val
    body = raw[m.end() :]
    return meta, body


class SkillService:
    def __init__(self, skills_root: str | Path | None = None):
        self.skills_root = Path(skills_root) if skills_root else Path(__file__).resolve().parents[2] / "skills"
        self._skills: dict[str, Skill] = {}
        self._by_domain: dict[str, list[str]] = {}

    def load_all(self) -> int:
        if not self.skills_root.exists():
            return 0
        count = 0
        for path in sorted(self.skills_root.rglob("SKILL.md")):
            try:
                self._load_one(path)
                count += 1
            except Exception:
                continue
        return count

    def _load_one(self, path: Path) -> Skill:
        raw = path.read_text(encoding="utf-8", errors="replace")
        meta, body = _parse_frontmatter(raw)
        domain = meta.get("domain") or path.parent.name
        name = meta.get("name") or path.parent.name
        skill_id = meta.get("id") or f"{domain}/{name}"
        description = meta.get("description") or f"Best practices for {name}"
        allowed = meta.get("allowed_tools") or []
        priority = int(meta.get("priority", 50))
        version = str(meta.get("version", "1.0"))

        skill = Skill(
            skill_id=skill_id,
            name=name,
            domain=domain,
            description=description,
            body=body.strip(),
            allowed_tools=list(allowed),
            priority=priority,
            version=version,
            metadata={"path": str(path)},
        )
        self._skills[skill.skill_id] = skill
        self._by_domain.setdefault(domain, []).append(skill.skill_id)
        return skill

    def get(self, skill_id: str) -> Skill | None:
        return self._skills.get(skill_id)

    def for_domain(self, domain: str) -> list[Skill]:
        ids = self._by_domain.get(domain, [])
        skills = [self._skills[i] for i in ids if i in self._skills]
        return sorted(skills, key=lambda s: s.priority, reverse=True)

    def primary_for_domain(self, domain: str) -> Skill | None:
        skills = self.for_domain(domain)
        return skills[0] if skills else None

    def list_ids(self) -> list[str]:
        return list(self._skills.keys())

    def list_domains(self) -> list[str]:
        return sorted(self._by_domain.keys())
