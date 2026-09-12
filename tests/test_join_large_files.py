from pathlib import Path
import subprocess
import sys


def test_join_large_files_rebuilds_launch_engine():
    root = Path(__file__).resolve().parents[1] / "desktop" / "parts"
    join = root / "join_large_files.py"
    assert join.is_file()
    parts = list(root.glob("launch_engine.py.part*"))
    assert parts, "expected launch_engine parts"
    out = root / "launch_engine.py"
    if out.exists():
        out.unlink()
    r = subprocess.run([sys.executable, str(join), "launch_engine.py"], cwd=root, check=True, capture_output=True, text=True)
    assert out.is_file()
    assert out.stat().st_size > 10000
    assert "wrote" in r.stdout
    out.unlink()


def test_join_parts_create_read_delete():
    root = Path(__file__).resolve().parents[1] / "desktop" / "parts"
    probe = root / "probe.txt.part01"
    probe.write_text("hello-part")
    join = root / "join_large_files.py"
    r = subprocess.run([sys.executable, str(join), "probe.txt"], cwd=root, check=True, capture_output=True, text=True)
    built = root / "probe.txt"
    assert built.read_text() == "hello-part"
    built.unlink()
    probe.unlink()
    assert not built.exists()
    assert "wrote" in r.stdout
