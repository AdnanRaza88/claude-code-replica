from pathlib import Path
import hashlib
import importlib.util
import sys


def _load():
    path = Path(__file__).resolve().parents[1] / "desktop" / "parts" / "join_large_files.py"
    spec = importlib.util.spec_from_file_location("join_large_files", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_expected_hashes_lists_slices():
    mod = _load()
    found = mod.expected_hashes()
    assert len(found) >= 2
    assert "launch_engine.py.part01" in found
    digest, size = found["launch_engine.py.part01"]
    assert len(digest) == 64
    assert size > 0
    assert size <= 8000


def test_join_rejects_bad_hash(tmp_path, monkeypatch):
    mod = _load()
    parts_dir = tmp_path / "parts"
    parts_dir.mkdir()
    payload = b"abc"
    name = "demo.py.part01"
    (parts_dir / name).write_bytes(payload)
    (parts_dir / "PARTS_SHA256.txt").write_text(
        f"{'0' * 64}  {name}  {len(payload)}\n", encoding="utf-8"
    )
    monkeypatch.setattr(mod, "root", parts_dir)
    try:
        mod.join("demo.py")
        raised = False
    except SystemExit:
        raised = True
    assert raised


def test_join_happy_path(tmp_path, monkeypatch):
    mod = _load()
    parts_dir = tmp_path / "parts"
    parts_dir.mkdir()
    a = b"hello "
    b = b"world"
    (parts_dir / "demo.py.part01").write_bytes(a)
    (parts_dir / "demo.py.part02").write_bytes(b)
    lines = [
        f"{hashlib.sha256(a).hexdigest()}  demo.py.part01  {len(a)}",
        f"{hashlib.sha256(b).hexdigest()}  demo.py.part02  {len(b)}",
    ]
    (parts_dir / "PARTS_SHA256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setattr(mod, "root", parts_dir)
    out = mod.join("demo.py")
    assert out.read_text(encoding="utf-8") == "hello world"
