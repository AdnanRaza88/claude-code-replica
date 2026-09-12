from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "launch_engine_min", ROOT / "desktop" / "launch_engine_min.py"
)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def test_read_version():
    v = mod.read_version()
    assert v.count(".") >= 1
    assert v[0].isdigit()


def test_pack_urls():
    assert mod._health_url("127.0.0.1", 8787).endswith("/health")
    assert mod._ui_url("127.0.0.1", 8787).endswith("/ui/")


def test_doctor_layout():
    report = mod.doctor("127.0.0.1", 8787)
    ids = {c["id"] for c in report["checks"]}
    assert "python" in ids
    assert "frontend" in ids
    assert "backend" in ids
    assert report["ok"] is True
