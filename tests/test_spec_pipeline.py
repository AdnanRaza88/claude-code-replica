"""F-033 spec-driven pipeline tests (improved templates + gates)."""
from __future__ import annotations

from pathlib import Path

from src.services.spec_service import (
    SpecService,
    STATUS_LOCKED,
    CORE_ARTIFACT_KINDS,
    ARTIFACT_KINDS,
)
from src.orchestration.planner import Planner


def test_create_project_includes_plan_template(tmp_path: Path):
    svc = SpecService(tmp_path)
    info = svc.create_project("Build a notes app with tags")
    arts = svc.list_artifacts(info["slug"])
    assert all(arts[k] for k in ARTIFACT_KINDS)
    prd = svc.read_artifact(info["slug"], "PRD")
    assert "Given" in prd and "WHEN" in prd
    intent = svc.read_artifact(info["slug"], "INTENT")
    assert "Open questions" in intent


def test_no_overwrite_existing(tmp_path: Path):
    svc = SpecService(tmp_path)
    slug = svc.create_project("x")["slug"]
    svc.write_artifact(slug, "INTENT", "custom intent")
    svc.create_project("x", slug=slug)
    assert svc.read_artifact(slug, "INTENT").strip() == "custom intent"


def test_placeholder_blocks_lock(tmp_path: Path):
    svc = SpecService(tmp_path)
    slug = svc.create_project("game")["slug"]
    report = svc.placeholder_report(slug)
    assert report  # templates still have placeholders
    try:
        svc.lock(slug)
        assert False, "should raise"
    except ValueError as e:
        assert "placeholder" in str(e).lower()


def test_lock_after_fill(tmp_path: Path):
    svc = SpecService(tmp_path)
    slug = svc.create_project("game")["slug"]
    for kind in CORE_ARTIFACT_KINDS:
        svc.write_artifact(
            slug,
            kind,
            f"# {kind}\n\nFilled content with no template markers.\nAcceptance: done.\n",
        )
    assert svc.placeholder_report(slug) == {}
    data = svc.lock(slug)
    assert data["status"] == STATUS_LOCKED
    assert (tmp_path / ".agentforge" / "BIBLE.md").is_file()
    ok, _ = svc.can_spawn_implementation(slug, strict=True)
    assert ok


def test_confirm_requires_fill(tmp_path: Path):
    svc = SpecService(tmp_path)
    slug = svc.create_project("app")["slug"]
    try:
        svc.confirm(slug)
        assert False
    except ValueError:
        pass


def test_planner_spec_request():
    p = Planner(strict_sdd=True)
    g = p.create_graph("s1", "Write a PRD and TRD for a chat app")
    assert len(g.tasks) == 1
    root = g.tasks[g.root_task_id]
    assert root.domain == "planning"
    assert "sdd/sdd" in (root.required_skills or [])


def test_planner_plan_mode():
    p = Planner()
    g = p.create_graph("s1", "implement payment API", mode="plan")
    root = g.tasks[g.root_task_id]
    assert root.domain == "planning"


def test_planner_strict_build_without_lock():
    p = Planner(strict_sdd=True)
    g = p.create_graph("s1", "implement and build a REST API", mode="agent", specs_locked=False)
    root = g.tasks[g.root_task_id]
    assert root.domain == "planning"
    assert "SDD gate" in root.objective


def test_planner_build_when_locked():
    p = Planner(strict_sdd=True)
    g = p.create_graph("s1", "implement payment API", mode="agent", specs_locked=True)
    root = g.tasks[g.root_task_id]
    assert root.domain in ("implementation", "orchestrator", "general", "backend")
