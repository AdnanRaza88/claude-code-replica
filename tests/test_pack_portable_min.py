from pathlib import Path
import importlib.util
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pack_portable_min", ROOT / "desktop" / "pack_portable_min.py"
)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def test_create_read_update_delete_pack():
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "pack"
        created = mod.layout_pack(dest)
        assert created["ok"] is True
        assert (dest / "frontend" / "index.html").is_file()
        assert (dest / "backend" / "main.py").is_file()
        assert (dest / "desktop" / "VERSION").is_file()
        assert (dest / "README-PORTABLE.txt").is_file()
        text = (dest / "README-PORTABLE.txt").read_text(encoding="utf-8")
        assert "AgentForge" in text
        zip_path = Path(tmp) / "pack.zip"
        zipped = mod.zip_pack(dest, zip_path)
        assert zipped["ok"] is True
        assert zipped["bytes"] > 0
        again = mod.layout_pack(dest)
        assert again["ok"] is True
        assert (dest / "frontend" / "index.html").is_file()
        assert mod.clear_pack(dest) is True
        assert dest.exists() is False
        assert zip_path.is_file()
