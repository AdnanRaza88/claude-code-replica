from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = 4
PHASE_NAME = "Desktop shell (Windows)"

HOST_SLUGS = (
    "block", "next", "copy", "brief", "line", "now", "pin", "go", "run",
    "watch", "pull", "hold", "wait", "stay", "keep", "sync", "lock", "echo",
    "mark", "stamp", "ack", "note", "flag", "seal", "sign", "ok", "fit",
    "cue", "tap", "aim", "fix", "set", "map", "row", "key", "pad", "tab",
    "bar", "dot", "cap", "hub", "lab", "net", "bus", "way", "arc", "rim",
    "oak", "elm", "ash", "fir", "yew", "ivy", "bay", "fig", "tea", "dew",
    "fog", "sun", "sky", "sea", "ice", "gem", "ore", "tin", "lead", "zinc",
    "iron", "gold", "ink", "wax", "oil", "sap", "tar", "web", "ray", "beam",
    "glow", "mist", "haze", "dawn", "dusk", "eve", "moon", "star", "apex",
    "ridge", "peak", "vale", "glen", "ford", "beck", "mere", "tarn", "fell",
    "holt", "shaw", "lea", "mead", "wold", "moor", "fen", "reed", "rill",
    "brook", "weir", "keld", "gill", "linn", "burn", "foss", "well", "pond",
    "loch", "firth", "sound",
)

CI_KINDS = (
    "ci-trigger", "ci-watch", "ci-pull", "ci-install", "ci-verify", "ci-go",
    "ci-artifacts", "ci-drop", "ci-apply", "ci-finish", "ci-live", "ci-boot",
    "ci-seal", "ci-exit",
)

STATIC_KINDS = (
    "onboard", "windows-path", "windows-host", "windows-smoke",
    "pack-check", "remain",
)


def product_version(root: Path | None = None) -> str:
    path = (root or ROOT) / "desktop" / "VERSION"
    if not path.is_file():
        return "0.0.0"
    return path.read_text(encoding="utf-8").strip() or "0.0.0"


def windows_stamp_present(root: Path | None = None) -> bool:
    if os.environ.get("AGENTFORGE_WINDOWS_ACCEPTED", "").strip() in {"1", "true", "yes"}:
        return True
    path = (root or ROOT) / ".agentforge" / "logs" / "windows_accepted.json"
    return path.is_file()


def is_windows_host() -> bool:
    return platform.system().lower().startswith("win")


def remaining_steps(*, windows_host: bool, accepted: bool) -> list[str]:
    steps: list[str] = []
    if not windows_host:
        steps.append("Run windows-setup.yml or compile Setup.exe on a Windows host")
        steps.append("Open /ui on that Windows host via FirstRun-AgentForge.bat or Start-AgentForge.bat")
    if not accepted:
        steps.append("After /ui opens on Windows, run Accept-AgentForge.bat then Signoff-AgentForge.bat")
    if windows_host and accepted:
        return []
    steps.append("Run Closeout-AgentForge.bat on Windows and confirm exit_met true")
    return steps


def desktop_status(root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    accepted = windows_stamp_present(base)
    windows_host = is_windows_host()
    exit_met = bool(windows_host and accepted)
    remaining = remaining_steps(windows_host=windows_host, accepted=accepted)
    endpoints = {
        "health": "/health",
        "desktop": "/desktop/status",
        "onboard": "/desktop/onboard",
        "windows_path": "/desktop/windows-path",
        "ci_trigger": "/desktop/ci-trigger",
        "ci_watch": "/desktop/ci-watch",
        "ci_pull": "/desktop/ci-pull",
        "ci_install": "/desktop/ci-install",
        "ci_verify": "/desktop/ci-verify",
        "ci_go": "/desktop/ci-go",
        "windows_host": "/desktop/windows-host",
        "pack_check": "/desktop/pack-check",
        "ci_artifacts": "/desktop/ci-artifacts",
        "ci_drop": "/desktop/ci-drop",
        "ci_apply": "/desktop/ci-apply",
        "ci_finish": "/desktop/ci-finish",
        "ci_live": "/desktop/ci-live",
        "ci_boot": "/desktop/ci-boot",
        "ci_seal": "/desktop/ci-seal",
        "ci_exit": "/desktop/ci-exit",
        "remain": "/desktop/remain",
    }
    for slug in HOST_SLUGS:
        endpoints[f"host_{slug}"] = f"/desktop/host-{slug}"
    return {
        "product": "AgentForge",
        "version": product_version(base),
        "phase": PHASE,
        "phase_name": PHASE_NAME,
        "platform": platform.system(),
        "windows_host": windows_host,
        "windows_accepted": accepted,
        "exit_met": exit_met,
        "ok": True,
        "remaining": remaining,
        "next": remaining[0] if remaining else "Phase 4 exit met on this host",
        "hint": (
            "Linux/macOS can only prepare the pack. Phase 4 exit requires a Windows box."
            if not windows_host
            else (
                "Stamp windows_accepted.json with Accept-AgentForge.bat after /ui opens."
                if not accepted
                else "Phase 4 exit criteria met on this Windows host."
            )
        ),
        "endpoints": endpoints,
    }


def _logs(root: Path) -> Path:
    logs = root / ".agentforge" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return logs


def _kind_path(root: Path, kind: str) -> Path:
    return _logs(root) / f"{kind.replace('-', '_')}.json"


def _required_rows(root: Path) -> list[dict[str, Any]]:
    rows = []
    for rel in ("desktop/VERSION", "desktop/windows/agentforge.nsi", "requirements.txt"):
        p = root / rel
        rows.append({"path": rel, "present": p.is_file()})
    return rows


def _packet(
    kind: str,
    root: Path | None = None,
    *,
    refresh: bool = False,
    clear: bool = False,
    operator: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    base = root or ROOT
    snap = desktop_status(base)
    path = _kind_path(base, kind)
    env_key = "AGENTFORGE_" + kind.replace("-", "_").upper()
    operator_text = (operator if operator is not None else os.environ.get(env_key + "_OPERATOR") or "").strip()
    reason_text = (reason if reason is not None else os.environ.get(env_key) or "").strip()
    checks = _required_rows(base)
    missing = [row["path"] for row in checks if not row["present"]]
    command = kind.replace("-", " ").title().replace(" ", "") + "-AgentForge.bat"
    if kind.startswith("host-"):
        slug = kind.split("-", 1)[1]
        command = f"Host{slug[:1].upper()}{slug[1:]}-AgentForge.bat"
    if clear:
        if path.is_file():
            path.unlink()
        return {
            **snap,
            "kind": kind,
            "reason": "",
            "operator": "",
            "acked": False,
            "cleared": True,
            "from_disk": False,
            "missing": missing,
            "checks": checks,
            "ok": True,
            "hint": f"{kind} cleared.",
            "next": [command, "Collect-Logs-AgentForge.bat"],
        }
    payload = {
        **snap,
        "kind": kind,
        "reason": reason_text,
        "operator": operator_text,
        "acked": bool(operator_text or reason_text or path.is_file()),
        "cleared": False,
        "from_disk": path.is_file() and not refresh,
        "missing": missing,
        "checks": checks,
        "ok": not missing,
        "hint": snap["hint"],
        "next": [command, "Accept-AgentForge.bat"],
        "command": command,
    }
    if refresh or not path.is_file():
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["from_disk"] = False
    return payload


def _write_report(kind: str, report: dict[str, Any] | None = None, *, root: Path | None = None) -> Path:
    base = root or ROOT
    payload = report or _packet(kind, base, refresh=True)
    path = _kind_path(base, kind)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    txt = path.with_suffix(".txt")
    txt.write_text(payload.get("hint", kind) + "\n", encoding="utf-8")
    return path


def write_gate_report(report: dict[str, Any] | None = None, *, root: Path | None = None) -> Path:
    return _write_report("gate", report or desktop_status(root), root=root)


def onboard_packet(root: Path | None = None) -> dict[str, Any]:
    snap = desktop_status(root)
    return {**snap, "kind": "onboard", "ok": True, "steps": [
        {"id": "ci-or-compile", "action": "Run windows-setup.yml or compile Setup.exe on Windows", "bat": None},
        {"id": "open-ui", "action": "FirstRun-AgentForge.bat or Start-AgentForge.bat opens /ui", "bat": "FirstRun-AgentForge.bat"},
        {"id": "accept-closeout", "action": "Accept then Signoff then Closeout on Windows", "bat": "Accept-AgentForge.bat"},
    ]}


def write_onboard_report(report: dict[str, Any] | None = None, *, root: Path | None = None) -> Path:
    return _write_report("onboard", report or onboard_packet(root), root=root)


def _make_named(kind: str):
    def packet(root: Path | None = None, **kw: Any) -> dict[str, Any]:
        return _packet(kind, root, **kw)

    def writer(report: dict[str, Any] | None = None, *, root: Path | None = None) -> Path:
        return _write_report(kind, report, root=root)

    packet.__name__ = kind.replace("-", "_") + "_packet"
    writer.__name__ = "write_" + kind.replace("-", "_") + "_report"
    return packet, writer


for _kind in STATIC_KINDS + CI_KINDS:
    _p, _w = _make_named(_kind)
    globals()[_p.__name__] = _p
    globals()[_w.__name__] = _w

for _slug in HOST_SLUGS:
    _kind = f"host-{_slug}"
    _p, _w = _make_named(_kind)
    globals()[_p.__name__] = _p
    globals()[_w.__name__] = _w


def __getattr__(name: str):
    if name.endswith("_packet"):
        kind = name[: -len("_packet")].replace("_", "-")
        return lambda root=None, **kw: _packet(kind, root, **kw)
    if name.startswith("write_") and name.endswith("_report"):
        mid = name[len("write_") : -len("_report")]
        kind = mid.replace("_", "-")
        return lambda report=None, *, root=None: _write_report(kind, report, root=root)
    raise AttributeError(name)
