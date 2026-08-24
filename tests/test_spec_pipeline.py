"""F-033 spec-driven pipeline tests."""
from __future__ import annotations

from pathlib import Path

from src.services.spec_service import SpecService, STATUS_LOCKED, ARTIFACT_KINDS
from src.orchestration.planner import Planner


def test_create_project_templates(tmp_path: Path):
    svc = SpecService(tmp_path)
    info = svc.create_project("Build a notes app with tags")
    assert info["slug"]
    arts = svc.list_artifacts(info["slug"])
    assert all(arts[k] for k in ARTIFACT_KINDS)
    assert "Acceptance" in svc.read_artifact(info["slug"], "PRD")


def test_no_overwrite_existing(tmp_path: Path):
    svc = SpecService(tmp_path)
    slug = svc.create_project("x")["slug"]
    svc.write_artifact(slug, "INTENT", "custom intent")
    svc.create_project("x", slug=slug)
    assert svc.read_artifact(slug, "INTENT").strip() == "custom intent"


def test_lock_requires_complete(tmp_path: Path):
    svc = SpecService(tmp_path)
    slug = "partial"
    (svc.specs_root / slug).mkdir(parents=True)
    try:
        svc.lock(slug)
        assert False, "should raise"
    except ValueError as e:
        assert "missing" in str(e).lower()


def test_lock_and_gate(tmp_path: Path):
    svc = SpecService(tmp_path)
    slug = svc.create_project("game")["slug"]
    ok, reason = svc.can_spawn_implementation(slug, strict=True)
    assert not ok
    svc.lock(slug)
    ok, reason = svc.can_spawn_implementation(slug, strict=True)
    assert ok
    assert svc.is_locked(slug)
    bible = tmp_path / ".agentforge" / "BIBLE.md"
    assert bible.is_file()


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
