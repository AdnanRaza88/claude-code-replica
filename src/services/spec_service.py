"""F-033 Spec-driven development artifacts under .agentforge/specs/."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARTIFACT_KINDS = ("INTENT", "PRD", "TRD", "WAVES", "BIBLE")

STATUS_DRAFT = "draft"
STATUS_CONFIRMED = "confirmed"
STATUS_LOCKED = "locked"


def _slugify(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "project").strip().lower()).strip("-")
    return (s or "project")[:max_len]


def template_intent(objective: str) -> str:
    return (
        "# Intent\n\n"
        f"**User ask:** {objective.strip()}\n\n"
        "**In one sentence:** _fill_\n\n"
        "**Who benefits:** _fill_\n\n"
        "**Success looks like:** _fill_\n\n"
        "**Out of scope (this pass):**\n- _fill_\n"
    )


def template_prd(objective: str) -> str:
    return (
        "# PRD-lite\n\n"
        f"**Objective:** {objective.strip()}\n\n"
        "## Goals\n"
        "- _goal 1_\n"
        "- _goal 2_\n\n"
        "## Non-goals\n"
        "- _explicit non-goal_\n\n"
        "## Users / context\n"
        "- _who_\n\n"
        "## Acceptance criteria\n"
        "- [ ] _testable criterion 1_\n"
        "- [ ] _testable criterion 2_\n"
        "- [ ] _testable criterion 3_\n\n"
        "## Constraints\n"
        "- _time / stack / policy_\n\n"
        "## Open questions\n"
        "- _question_\n"
    )


def template_trd(objective: str) -> str:
    return (
        "# TRD-lite\n\n"
        f"**Objective:** {objective.strip()}\n\n"
        "## Stack\n"
        "- Language / runtime: _fill_\n"
        "- Key libraries: _fill_\n\n"
        "## Modules / layout\n"
        "- `path/` — responsibility\n\n"
        "## Interfaces (contracts)\n"
        "- `Name` — inputs → outputs; errors\n\n"
        "## Data / state\n"
        "- _what persists_\n\n"
        "## Dependencies between modules\n"
        "- A before B because _reason_\n\n"
        "## Risks\n"
        "- _risk_ → mitigation\n"
    )


def template_waves(objective: str) -> str:
    return (
        "# Task waves\n\n"
        f"**Objective:** {objective.strip()}\n\n"
        "Rules: parallel only when no shared file/API dependency; bible locked first.\n\n"
        "## Wave 0 — Spec lock\n"
        "- [ ] Intent / PRD / TRD reviewed\n"
        "- [ ] Bible locked\n\n"
        "## Wave 1 — Foundation (sequence or parallel)\n"
        "| Task | Domain | Depends on | Acceptance line |\n"
        "|------|--------|------------|-----------------|\n"
        "| _task_ | implementation | — | PRD #1 |\n\n"
        "## Wave 2 — Parallel feature slices\n"
        "| Task | Domain | Depends on | Acceptance line |\n"
        "|------|--------|------------|-----------------|\n"
        "| _task_ | frontend | Wave 1 contracts | PRD #2 |\n\n"
        "## Wave 3 — Verify barrier\n"
        "- [ ] Acceptance criteria checked\n"
        "- [ ] Bible contradictions none\n"
    )


def template_bible(objective: str) -> str:
    return (
        "# Project bible (locked contract)\n\n"
        f"**For:** {objective.strip()}\n\n"
        "## Theme / tone\n"
        "- _one theme — all agents obey_\n\n"
        "## Stack (do not invent alternatives)\n"
        "- _stack_\n\n"
        "## Naming\n"
        "- Files: _convention_\n"
        "- Symbols: _convention_\n\n"
        "## Layout\n"
        "- _where code lives_\n\n"
        "## Non-goals\n"
        "- _do not build_\n\n"
        "## Acceptance anchors\n"
        "- _mirror PRD lines_\n\n"
        "## Parallel rules\n"
        "- No parallel writes to the same file\n"
        "- Shared types/APIs owned by one task first\n"
    )


TEMPLATES = {
    "INTENT": template_intent,
    "PRD": template_prd,
    "TRD": template_trd,
    "WAVES": template_waves,
    "BIBLE": template_bible,
}


class SpecService:
    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.specs_root = self.project_root / ".agentforge" / "specs"

    def set_project_root(self, root: str | Path) -> None:
        self.project_root = Path(root)
        self.specs_root = self.project_root / ".agentforge" / "specs"

    def ensure_roots(self) -> None:
        self.specs_root.mkdir(parents=True, exist_ok=True)

    def slug_for(self, objective: str) -> str:
        return _slugify(objective)

    def project_dir(self, slug: str) -> Path:
        return self.specs_root / slug

    def create_project(self, objective: str, slug: str | None = None) -> dict[str, Any]:
        """Create draft spec pack with short templates. Does not overwrite existing artifacts."""
        self.ensure_roots()
        slug = slug or self.slug_for(objective)
        d = self.project_dir(slug)
        d.mkdir(parents=True, exist_ok=True)
        created: list[str] = []
        for kind, fn in TEMPLATES.items():
            path = d / f"{kind}.md"
            if not path.exists():
                path.write_text(fn(objective), encoding="utf-8")
                created.append(kind)
        status_path = d / "STATUS.json"
        if not status_path.exists():
            self._write_status(slug, STATUS_DRAFT, objective=objective)
        return {
            "slug": slug,
            "path": str(d),
            "created": created,
            "status": self.get_status(slug),
        }

    def _status_path(self, slug: str) -> Path:
        return self.project_dir(slug) / "STATUS.json"

    def _write_status(self, slug: str, status: str, **extra: Any) -> dict[str, Any]:
        data = {
            "slug": slug,
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **extra,
        }
        prev = self.get_status(slug)
        if prev:
            for k, v in prev.items():
                if k not in data:
                    data[k] = v
        data["status"] = status
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.project_dir(slug).mkdir(parents=True, exist_ok=True)
        self._status_path(slug).write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def get_status(self, slug: str) -> dict[str, Any] | None:
        p = self._status_path(slug)
        if not p.is_file():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def write_artifact(self, slug: str, kind: str, content: str, *, overwrite: bool = True) -> Path:
        kind = kind.upper().replace(".MD", "")
        if kind not in ARTIFACT_KINDS:
            raise ValueError(f"unknown artifact kind: {kind}")
        d = self.project_dir(slug)
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"{kind}.md"
        if path.exists() and not overwrite:
            return path
        path.write_text(content.strip() + "\n", encoding="utf-8")
        return path

    def read_artifact(self, slug: str, kind: str) -> str:
        kind = kind.upper().replace(".MD", "")
        path = self.project_dir(slug) / f"{kind}.md"
        if not path.is_file():
            return ""
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def list_artifacts(self, slug: str) -> dict[str, bool]:
        d = self.project_dir(slug)
        return {k: (d / f"{k}.md").is_file() for k in ARTIFACT_KINDS}

    def is_complete(self, slug: str) -> bool:
        arts = self.list_artifacts(slug)
        return all(arts.get(k) for k in ARTIFACT_KINDS)

    def is_locked(self, slug: str) -> bool:
        st = self.get_status(slug)
        return bool(st and st.get("status") == STATUS_LOCKED)

    def confirm(self, slug: str) -> dict[str, Any]:
        if not self.is_complete(slug):
            missing = [k for k, ok in self.list_artifacts(slug).items() if not ok]
            raise ValueError(f"cannot confirm; missing artifacts: {missing}")
        return self._write_status(slug, STATUS_CONFIRMED)

    def lock(self, slug: str, *, copy_bible_to_root: bool = True) -> dict[str, Any]:
        if not self.is_complete(slug):
            missing = [k for k, ok in self.list_artifacts(slug).items() if not ok]
            raise ValueError(f"cannot lock; missing artifacts: {missing}")
        data = self._write_status(slug, STATUS_LOCKED)
        if copy_bible_to_root:
            bible = self.read_artifact(slug, "BIBLE")
            if bible:
                root_bible_dir = self.project_root / ".agentforge"
                root_bible_dir.mkdir(parents=True, exist_ok=True)
                root_bible = root_bible_dir / "BIBLE.md"
                # Do not overwrite existing root bible silently
                if not root_bible.exists():
                    root_bible.write_text(bible, encoding="utf-8")
        return data

    def list_projects(self) -> list[dict[str, Any]]:
        self.ensure_roots()
        out = []
        if not self.specs_root.exists():
            return out
        for d in sorted(self.specs_root.iterdir()):
            if not d.is_dir():
                continue
            st = self.get_status(d.name) or {"slug": d.name, "status": "unknown"}
            st["artifacts"] = self.list_artifacts(d.name)
            out.append(st)
        return out

    def can_spawn_implementation(self, slug: str | None, *, strict: bool = True) -> tuple[bool, str]:
        """Gate parallel code work until specs+bible locked (when strict)."""
        if not strict:
            return True, "strictness off"
        if not slug:
            return False, "no spec project slug; run plan/spec phase first"
        if not self.is_complete(slug):
            missing = [k for k, ok in self.list_artifacts(slug).items() if not ok]
            return False, f"specs incomplete: missing {missing}"
        if not self.is_locked(slug):
            return False, f"specs not locked (status={(self.get_status(slug) or {}).get('status')})"
        return True, "locked"

    def prompt_block_for_agents(self, slug: str | None) -> str:
        """Short contract block to inject when slug known."""
        if not slug:
            return ""
        parts = []
        for kind in ARTIFACT_KINDS:
            body = self.read_artifact(slug, kind)
            if not body:
                continue
            # keep injection small
            clipped = body.strip()
            if len(clipped) > 2500:
                clipped = clipped[:2500] + "\n...[truncated]..."
            parts.append(f"### Spec:{kind}\n{clipped}")
        st = self.get_status(slug)
        header = f"## Active specs (`{slug}` status={(st or {}).get('status', '?')})\n"
        return header + "\n\n".join(parts) if parts else ""
