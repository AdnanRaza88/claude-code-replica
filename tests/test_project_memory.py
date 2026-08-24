"""F-020 project memory + F-031 bible — engine tests."""
from __future__ import annotations

from pathlib import Path

from src.services.context_service import ContextService, MEMORY_CANDIDATES, BIBLE_CANDIDATES


def test_missing_memory_is_empty(tmp_path: Path):
    ctx = ContextService(project_root=tmp_path)
    assert ctx.load_project_memory() == ""
    assert ctx.memory_meta()["memory_source"] is None


def test_loads_claude_md(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("# Rules\n- Use pathlib\n- No secrets", encoding="utf-8")
    ctx = ContextService(project_root=tmp_path)
    text = ctx.load_project_memory()
    assert "pathlib" in text
    assert ctx.memory_meta()["memory_source"] == "CLAUDE.md"


def test_agents_md_fallback(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("Prefer small PRs", encoding="utf-8")
    ctx = ContextService(project_root=tmp_path)
    assert "small PRs" in ctx.load_project_memory()
    assert ctx.memory_meta()["memory_source"] == "AGENTS.md"


def test_claude_wins_over_agents(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("from-claude", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("from-agents", encoding="utf-8")
    ctx = ContextService(project_root=tmp_path)
    assert ctx.load_project_memory() == "from-claude"


def test_memory_cap(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("x" * 50_000, encoding="utf-8")
    ctx = ContextService(project_root=tmp_path)
    text = ctx.load_project_memory(max_chars=100)
    assert len(text) < 200
    assert "truncated" in text


def test_bible_load(tmp_path: Path):
    agentforge = tmp_path / ".agentforge"
    agentforge.mkdir()
    (agentforge / "BIBLE.md").write_text("Stack: Python. Theme: dark.", encoding="utf-8")
    ctx = ContextService(project_root=tmp_path)
    assert "Python" in ctx.load_project_bible()
    assert ctx.memory_meta()["bible_source"] == ".agentforge/BIBLE.md"


def test_set_bible_no_silent_overwrite(tmp_path: Path):
    ctx = ContextService(project_root=tmp_path)
    assert ctx.set_project_bible("first") is True
    assert ctx.set_project_bible("second") is False
    assert ctx.get_project_bible() == "first"
    assert ctx.set_project_bible("second", force=True) is True
    assert ctx.get_project_bible() == "second"


def test_build_pack_injects_memory_and_bible(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("Always cite sources", encoding="utf-8")
    (tmp_path / "BIBLE.md").write_text("Name: replica", encoding="utf-8")
    ctx = ContextService(project_root=tmp_path)
    pack = ctx.build_pack(domain="general", objective="test")
    assert "Always cite sources" in pack.project_memory
    assert "Name: replica" in pack.project_bible
    block = pack.to_prompt_block()
    assert "Project memory" in block
    assert "Project bible" in block
    assert "Always cite sources" in block


def test_candidates_order():
    assert MEMORY_CANDIDATES[0] == "CLAUDE.md"
    assert BIBLE_CANDIDATES[0] == ".agentforge/BIBLE.md"
