import tempfile
from pathlib import Path

from src.services.session_memory import SessionMemoryService


def test_record_list_files_recall():
    with tempfile.TemporaryDirectory() as d:
        sm = SessionMemoryService(project_root=d)
        sm.record(
            objective="Fix auth refresh",
            summary="edge case still failing",
            files=["src/auth/refresh.py", "tests/test_refresh.py"],
            tools=["read", "edit"],
        )
        sm.record(
            objective="Add redis cache",
            summary="wired redis client",
            files=["src/cache/redis.py"],
            tools=["write"],
        )
        recent = sm.list_recent(5)
        assert len(recent) == 2
        files = sm.files_recent(10)
        assert "src/auth/refresh.py" in files
        hits = sm.recall("auth")
        assert hits
        assert any("auth" in (h.get("objective") or "").lower() for h in hits)
        block = sm.wake_block(3)
        assert "Recent sessions" in block
        assert (Path(d) / ".agentforge" / "session_memory" / "episodes.jsonl").exists()


def test_empty_formats():
    with tempfile.TemporaryDirectory() as d:
        sm = SessionMemoryService(project_root=d)
        assert "No session" in sm.format_list()
        assert "No files" in sm.format_files()
