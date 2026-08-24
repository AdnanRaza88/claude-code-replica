"""F-033 Spec-driven development artifacts under .agentforge/specs/.

Aligned with Spec Kit / Claude / Agent Factory practices:
Constitution (CLAUDE.md) stays project-level; feature pack is
Intent → PRD → TRD → WAVES → BIBLE → PLAN (post-lock implementation plan).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Core pack required before confirm/lock. PLAN is optional until after lock.
CORE_ARTIFACT_KINDS = ("INTENT", "PRD", "TRD", "WAVES", "BIBLE")
OPTIONAL_ARTIFACT_KINDS = ("PLAN",)
ARTIFACT_KINDS = CORE_ARTIFACT_KINDS + OPTIONAL_ARTIFACT_KINDS

STATUS_DRAFT = "draft"
STATUS_CLARIFIED = "clarified"
STATUS_CONFIRMED = "confirmed"
STATUS_LOCKED = "locked"
STATUS_IN_PROGRESS = "in_progress"
STATUS_DONE = "done"

VALID_STATUSES = (
    STATUS_DRAFT,
    STATUS_CLARIFIED,
    STATUS_CONFIRMED,
    STATUS_LOCKED,
    STATUS_IN_PROGRESS,
    STATUS_DONE,
)

_PLACEHOLDER_RE = re.compile(
    r"_fill_|_goal |_explicit |_who_|_testable |_question_|_task_"
    r"|_stack_|_convention_|_do not build_|_mirror |_risk_|_path/",
    re.I,
)


def _slugify(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "project").strip().lower()).strip("-")
    return (s or "project")[:max_len]


def template_intent(objective: str) -> str:
    return (
        "# Intent\n\n"
        "> What / why only. No stack, no file paths, no implementation.\n\n"
        f"**User ask:** {objective.strip()}\n\n"
        "**In one sentence:** _fill_\n\n"
        "**Problem:** _what pain or gap_\n\n"
        "**Who benefits:** _primary user_\n\n"
        "**Success looks like:** _observable outcome_\n\n"
        "**Out of scope (this pass):**\n"
        "- _must list at least one non-goal_\n\n"
        "## Open questions (required if anything is ambiguous)\n"
        "- _hard question the user must answer before lock_\n"
        "- _another assumption to confirm_\n\n"
        "## Interview notes\n"
        "- Q: … A: …\n"
    )


def template_prd(objective: str) -> str:
    return (
        "# PRD-lite (Specify)\n\n"
        "> Product contract: testable acceptance + examples. Not a novel.\n\n"
        f"**Objective:** {objective.strip()}\n\n"
        "## Goals\n"
        "- _goal 1 — user outcome_\n"
        "- _goal 2_\n\n"
        "## Non-goals\n"
        "- _explicit non-goal (prevents vibe scope)_\n\n"
        "## Users / context\n"
        "- _who, when, where_\n\n"
        "## Functional requirements\n"
        "Use EARS where possible: WHEN [condition] THE SYSTEM SHALL [behavior].\n\n"
        "1. WHEN _condition_ THE SYSTEM SHALL _behavior_\n"
        "2. WHEN _condition_ THE SYSTEM SHALL _behavior_\n\n"
        "## Acceptance criteria (checkboxes — each must be verifiable)\n"
        "- [ ] AC1: _measurable_\n"
        "- [ ] AC2: _measurable_\n"
        "- [ ] AC3: _measurable_\n\n"
        "## Examples (input → output)\n"
        "### Example 1\n"
        "- **Given:** _precondition_\n"
        "- **When:** _action_\n"
        "- **Then:** _observable result_\n\n"
        "### Example 2\n"
        "- **Given:** _precondition_\n"
        "- **When:** _action_\n"
        "- **Then:** _observable result_\n\n"
        "## Constraints / NFRs\n"
        "- Performance: _e.g. p95 < …_\n"
        "- Security / privacy: _fill_\n"
        "- Compatibility: _fill_\n\n"
        "## Open questions\n"
        "- _question_\n"
    )


def template_trd(objective: str) -> str:
    return (
        "# TRD-lite (Design)\n\n"
        "> How, at contract level. Interfaces and ownership — not full source code.\n\n"
        f"**Objective:** {objective.strip()}\n\n"
        "## Stack (locked for this feature)\n"
        "- Language / runtime: _fill_\n"
        "- Key libraries: _fill_\n"
        "- Do not introduce alternatives without updating this doc\n\n"
        "## Modules / layout\n"
        "| Path | Responsibility | Owner task |\n"
        "|------|----------------|------------|\n"
        "| `path/` | _what_ | Wave 1 |\n\n"
        "## Interfaces (contracts)\n"
        "- `Name(inputs) → outputs` · errors: _list_\n\n"
        "## Data / state\n"
        "- Entities / fields: _fill_\n"
        "- What persists vs ephemeral: _fill_\n\n"
        "## Dependencies\n"
        "- A before B because _reason_\n"
        "- Shared types owned by: _one task only_\n\n"
        "## Risks\n"
        "- _risk_ → mitigation\n\n"
        "## Test strategy (maps to PRD ACs)\n"
        "- AC1 → _how verified_\n"
        "- AC2 → _how verified_\n"
    )


def template_waves(objective: str) -> str:
    return (
        "# Task waves (Tasks)\n\n"
        f"**Objective:** {objective.strip()}\n\n"
        "Rules:\n"
        "- Parallel only when no shared file/API ownership conflict.\n"
        "- Bible must be locked before Wave 1 code.\n"
        "- Every task links to a PRD acceptance line (ACn).\n"
        "- Barrier: do not start next wave until checklist passes.\n\n"
        "## Wave 0 — Spec lock (sequence)\n"
        "- [ ] Intent clarified (open questions answered)\n"
        "- [ ] PRD acceptance + examples reviewed\n"
        "- [ ] TRD interfaces reviewed\n"
        "- [ ] Bible locked\n\n"
        "## Wave 1 — Foundation\n"
        "| ID | Task | Domain | Depends | AC | Parallel? |\n"
        "|----|------|--------|---------|----|-----------|\n"
        "| T1 | _task_ | implementation | — | AC1 | no |\n\n"
        "### Barrier 1\n"
        "- [ ] T1 done and AC1 holds\n"
        "- [ ] No bible contradiction\n\n"
        "## Wave 2 — Parallel slices (if independent)\n"
        "| ID | Task | Domain | Depends | AC | Parallel? |\n"
        "|----|------|--------|---------|----|-----------|\n"
        "| T2 | _task_ | frontend | T1 | AC2 | yes with T3 |\n"
        "| T3 | _task_ | backend | T1 | AC3 | yes with T2 |\n\n"
        "### Barrier 2\n"
        "- [ ] Linked ACs pass\n"
        "- [ ] Integrator: theme/stack match bible\n\n"
        "## Wave 3 — Verify\n"
        "- [ ] All PRD acceptance checkboxes\n"
        "- [ ] Examples from PRD reproduced\n"
        "- [ ] Open questions closed or deferred in writing\n"
    )


def template_bible(objective: str) -> str:
    return (
        "# Project bible (locked contract)\n\n"
        "> Single theme + stack + naming. All parallel agents obey this.\n\n"
        f"**For:** {objective.strip()}\n\n"
        "## Theme / tone\n"
        "- _one theme — do not invent a second_\n\n"
        "## Stack (do not invent alternatives)\n"
        "- _stack from TRD_\n\n"
        "## Naming\n"
        "- Files: _convention_\n"
        "- Symbols: _convention_\n\n"
        "## Layout\n"
        "- _where code lives_\n\n"
        "## Non-goals\n"
        "- _from Intent/PRD_\n\n"
        "## Acceptance anchors\n"
        "- AC1: _mirror PRD_\n"
        "- AC2: _mirror PRD_\n\n"
        "## Parallel rules\n"
        "- No parallel writes to the same file\n"
        "- Shared types/APIs owned by one task first\n"
        "- On contradiction with this bible: stop and surface, do not merge silently\n"
    )


def template_plan(objective: str) -> str:
    return (
        "# Implementation plan (PLAN)\n\n"
        "> File-level plan after lock, before code. Smart-kid test: another eng could execute this.\n\n"
        f"**Objective:** {objective.strip()}\n\n"
        "## Order of work\n"
        "1. _step — files — test_\n"
        "2. _step — files — test_\n\n"
        "## Files touched\n"
        "| File | Change | Wave |\n"
        "|------|--------|------|\n"
        "| `path` | _what_ | 1 |\n\n"
        "## Risks / rollback\n"
        "- _risk_ → _rollback_\n\n"
        "## Done when\n"
        "- [ ] All linked ACs green\n"
        "- [ ] PLAN steps checked off\n"
    )


TEMPLATES = {
    "INTENT": template_intent,
    "PRD": template_prd,
    "TRD": template_trd,
    "WAVES": template_waves,
    "BIBLE": template_bible,
    "PLAN": template_plan,
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
        """Create draft pack. Does not overwrite existing artifact files."""
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
        if not self._status_path(slug).exists():
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
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid status: {status}")
        data: dict[str, Any] = {}
        prev = self.get_status(slug)
        if prev:
            data.update(prev)
        data.update(extra)
        data["slug"] = slug
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
        """Core five present (PLAN optional)."""
        arts = self.list_artifacts(slug)
        return all(arts.get(k) for k in CORE_ARTIFACT_KINDS)

    def is_locked(self, slug: str) -> bool:
        st = self.get_status(slug)
        return bool(st and st.get("status") in (STATUS_LOCKED, STATUS_IN_PROGRESS, STATUS_DONE))

    def placeholder_report(self, slug: str) -> dict[str, list[str]]:
        """Surfaces remaining _fill_ style placeholders per core artifact."""
        report: dict[str, list[str]] = {}
        for kind in CORE_ARTIFACT_KINDS:
            body = self.read_artifact(slug, kind)
            if not body:
                report[kind] = ["(missing file)"]
                continue
            hits = sorted(set(_PLACEHOLDER_RE.findall(body)))
            if hits:
                report[kind] = hits
        return report

    def mark_clarified(self, slug: str) -> dict[str, Any]:
        if not self.is_complete(slug):
            missing = [k for k, ok in self.list_artifacts(slug).items() if k in CORE_ARTIFACT_KINDS and not ok]
            raise ValueError(f"cannot clarify; missing: {missing}")
        return self._write_status(slug, STATUS_CLARIFIED)

    def confirm(self, slug: str, *, allow_placeholders: bool = False) -> dict[str, Any]:
        if not self.is_complete(slug):
            missing = [k for k, ok in self.list_artifacts(slug).items() if k in CORE_ARTIFACT_KINDS and not ok]
            raise ValueError(f"cannot confirm; missing artifacts: {missing}")
        if not allow_placeholders:
            left = self.placeholder_report(slug)
            if left:
                raise ValueError(
                    "cannot confirm; placeholders remain: "
                    + ", ".join(f"{k}:{v}" for k, v in left.items())
                )
        return self._write_status(slug, STATUS_CONFIRMED)

    def lock(self, slug: str, *, copy_bible_to_root: bool = True, allow_placeholders: bool = False) -> dict[str, Any]:
        if not self.is_complete(slug):
            missing = [k for k, ok in self.list_artifacts(slug).items() if k in CORE_ARTIFACT_KINDS and not ok]
            raise ValueError(f"cannot lock; missing artifacts: {missing}")
        if not allow_placeholders:
            left = self.placeholder_report(slug)
            if left:
                raise ValueError(
                    "cannot lock; placeholders remain: "
                    + ", ".join(f"{k}:{v}" for k, v in left.items())
                )
        data = self._write_status(slug, STATUS_LOCKED)
        if copy_bible_to_root:
            bible = self.read_artifact(slug, "BIBLE")
            if bible:
                root_bible_dir = self.project_root / ".agentforge"
                root_bible_dir.mkdir(parents=True, exist_ok=True)
                root_bible = root_bible_dir / "BIBLE.md"
                if not root_bible.exists():
                    root_bible.write_text(bible, encoding="utf-8")
        # Ensure PLAN template exists after lock
        plan_path = self.project_dir(slug) / "PLAN.md"
        if not plan_path.exists():
            obj = (self.get_status(slug) or {}).get("objective") or slug
            plan_path.write_text(template_plan(str(obj)), encoding="utf-8")
        return data

    def mark_in_progress(self, slug: str) -> dict[str, Any]:
        if not self.is_locked(slug):
            raise ValueError("lock specs before in_progress")
        return self._write_status(slug, STATUS_IN_PROGRESS)

    def mark_done(self, slug: str) -> dict[str, Any]:
        if not self.is_locked(slug):
            raise ValueError("lock specs before done")
        return self._write_status(slug, STATUS_DONE)

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
        if not strict:
            return True, "strictness off"
        if not slug:
            return False, "no spec project slug; run plan/spec phase first"
        if not self.is_complete(slug):
            missing = [k for k in CORE_ARTIFACT_KINDS if not self.list_artifacts(slug).get(k)]
            return False, f"specs incomplete: missing {missing}"
        if not self.is_locked(slug):
            return False, f"specs not locked (status={(self.get_status(slug) or {}).get('status')})"
        return True, "locked"

    def prompt_block_for_agents(self, slug: str | None, *, max_chars_each: int = 2200) -> str:
        if not slug:
            return ""
        # Prefer bible + PRD acceptance density for implementers
        order = ("BIBLE", "PRD", "TRD", "WAVES", "PLAN", "INTENT")
        parts = []
        for kind in order:
            body = self.read_artifact(slug, kind)
            if not body:
                continue
            clipped = body.strip()
            if len(clipped) > max_chars_each:
                clipped = clipped[:max_chars_each] + "\n...[truncated]..."
            parts.append(f"### Spec:{kind}\n{clipped}")
        st = self.get_status(slug)
        header = f"## Active specs (`{slug}` status={(st or {}).get('status', '?')})\n"
        return header + "\n\n".join(parts) if parts else ""
