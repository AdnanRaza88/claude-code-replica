import json
from pathlib import Path

from src.services.desktop_status import (
    desktop_status,
    host_sound_packet,
    product_version,
    write_host_sound_report,
)


def test_product_version_matches_file():
    ver = product_version()
    assert ver == Path("desktop/VERSION").read_text(encoding="utf-8").strip()
    assert ver.startswith("0.")


def test_desktop_status_linux_cannot_exit(tmp_path, monkeypatch):
    (tmp_path / "desktop").mkdir()
    (tmp_path / "desktop" / "VERSION").write_text("0.5.56\n", encoding="utf-8")
    monkeypatch.delenv("AGENTFORGE_WINDOWS_ACCEPTED", raising=False)
    snap = desktop_status(tmp_path)
    assert snap["ok"] is True
    assert snap["product"] == "AgentForge"
    assert snap["exit_met"] is False or snap["windows_host"] is True


def test_host_sound_crud(tmp_path):
    (tmp_path / "desktop").mkdir()
    (tmp_path / "desktop" / "VERSION").write_text("0.5.56\n", encoding="utf-8")
    created = host_sound_packet(tmp_path, refresh=True, operator="ops", reason="gate")
    assert created["kind"] == "host-sound"
    assert created["operator"] == "ops"
    path = write_host_sound_report(created, root=tmp_path)
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["kind"] == "host-sound"
    updated = host_sound_packet(tmp_path, refresh=True, operator="ops2", reason="retry")
    assert updated["operator"] == "ops2"
    cleared = host_sound_packet(tmp_path, clear=True)
    assert cleared["cleared"] is True
    miss = host_sound_packet(tmp_path)
    assert miss["cleared"] is False
