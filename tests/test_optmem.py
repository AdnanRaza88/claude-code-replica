import tempfile
from pathlib import Path

from src.services.optmem_service import OptMemStore


def test_init_note_wake_recall():
    with tempfile.TemporaryDirectory() as d:
        store = OptMemStore(project_root=d)
        assert not store.exists()
        store.init()
        assert store.exists()
        r = store.note("User prefers Python 3.12")
        assert r["index"] == 0
        store.note("Project uses Streamlit temporarily")
        store.note("Next feature is F-031 shared bible")
        wake = store.wake()
        assert "Python 3.12" in wake
        assert store.count() == 3
        hits = store.recall("Python")
        assert "#0" in hits
        hits2 = store.recall("bible")
        assert "F-031" in hits2


def test_nap_and_zoom():
    with tempfile.TemporaryDirectory() as d:
        store = OptMemStore(project_root=d)
        store.init()
        store.note("fact A about auth")
        store.note("fact B about auth jwt")
        store.note("fact C unrelated")
        store.note("fact D unrelated")
        pending = store._pending(limit=5)
        assert any(hi - lo == 2 for lo, hi in pending)
        lo, hi = next(p for p in pending if p[1] - p[0] == 2)
        result = store.nap(lo, hi, "auth uses jwt")
        assert result.get("ok")
        z = store.zoom(lo, hi)
        assert "auth" in z.lower() or "jwt" in z.lower() or "#" in z


def test_memory_under_agentforge():
    with tempfile.TemporaryDirectory() as d:
        store = OptMemStore(project_root=d)
        store.init()
        assert (Path(d) / ".agentforge" / "optmem" / "LOG.txt").exists()
