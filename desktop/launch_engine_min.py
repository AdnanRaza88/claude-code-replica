from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT_FILE = ROOT / ".agentforge" / "engine.port"
LOCK_FILE = ROOT / ".agentforge" / "engine.lock"
CHILD_FILE = ROOT / ".agentforge" / "engine.child"
LOG_FILE = ROOT / ".agentforge" / "logs" / "engine.log"


def log_line(msg: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}\n")


def lock_stale(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        pid = int(path.read_text(encoding="utf-8").strip() or "0")
    except ValueError:
        return True
    if pid <= 0:
        return True
    try:
        os.kill(pid, 0)
        return False
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    except OSError:
        return True


def acquire_lock() -> bool:
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_FILE.exists() and not lock_stale(LOCK_FILE):
        return False
    LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8")
    return True


def release_lock(force: bool = False) -> None:
    try:
        if not LOCK_FILE.exists():
            return
        stored = LOCK_FILE.read_text(encoding="utf-8").strip()
        if force or stored == str(os.getpid()):
            LOCK_FILE.unlink()
    except OSError:
        pass


def _health_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/health"


def _ui_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/ui/"


def port_free(host: str, port: int) -> bool:
    family = socket.AF_INET6 if ":" in host and host != "127.0.0.1" else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def wait_healthy(host: str, port: int, timeout: float = 30.0) -> bool:
    url = _health_url(host, port)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.25)
    return False


def pick_bind(host: str, preferred: int, span: int = 5) -> tuple[int, str]:
    for offset in range(span + 1):
        port = preferred + offset
        if wait_healthy(host, port, timeout=0.6):
            return port, "attach"
        if port_free(host, port):
            return port, "spawn"
    return preferred, "busy"


def write_port_file(port: int) -> None:
    PORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PORT_FILE.write_text(str(port), encoding="utf-8")


def read_port_file() -> int | None:
    if not PORT_FILE.exists():
        return None
    try:
        value = int(PORT_FILE.read_text(encoding="utf-8").strip())
    except ValueError:
        return None
    return value if value > 0 else None


def _read_pid(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        pid = int(path.read_text(encoding="utf-8").strip() or "0")
    except ValueError:
        return None
    return pid if pid > 0 else None


def write_child(pid: int) -> None:
    CHILD_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHILD_FILE.write_text(str(pid), encoding="utf-8")


def clear_child() -> None:
    try:
        if CHILD_FILE.exists():
            CHILD_FILE.unlink()
    except OSError:
        pass


def engine_status(host: str, preferred: int) -> dict:
    port = read_port_file() or preferred
    return {
        "host": host,
        "port": port,
        "healthy": wait_healthy(host, port, timeout=0.6),
        "pid": _read_pid(LOCK_FILE),
        "lock_stale": lock_stale(LOCK_FILE),
        "ui": _ui_url(host, port),
    }


def read_version() -> str:
    path = ROOT / "desktop" / "VERSION"
    if not path.is_file():
        return "0.0.0"
    return path.read_text(encoding="utf-8").strip() or "0.0.0"


def doctor(host: str, preferred: int) -> dict:
    checks = [
        {"id": "python", "ok": sys.version_info >= (3, 11), "detail": sys.version.split()[0]},
        {"id": "frontend", "ok": (ROOT / "frontend" / "index.html").is_file(), "detail": "index.html"},
        {"id": "backend", "ok": (ROOT / "backend" / "main.py").is_file(), "detail": "main.py"},
        {"id": "version", "ok": True, "detail": read_version()},
    ]
    info = engine_status(host, preferred)
    checks.append({"id": "engine", "ok": info["healthy"], "detail": info["ui"]})
    ok = all(c["ok"] for c in checks if c["id"] != "engine")
    return {"ok": ok, "ready": info["healthy"], "checks": checks, "version": read_version()}


def stop_engine(host: str, preferred: int) -> int:
    pid = _read_pid(CHILD_FILE) or _read_pid(LOCK_FILE)
    if pid:
        try:
            os.kill(pid, 15)
        except OSError:
            pass
        time.sleep(0.4)
    clear_child()
    release_lock(force=True)
    print("stopped", flush=True)
    return 0


def spawn_engine(host: str, preferred: int, reload: bool = False) -> int:
    if not acquire_lock():
        port, mode = pick_bind(host, preferred)
        if mode == "attach":
            write_port_file(port)
            print(f"AgentForge engine already up {_ui_url(host, port)}", flush=True)
            return 0
        print("AgentForge engine already starting (lock held)", file=sys.stderr)
        return 4
    port, mode = pick_bind(host, preferred)
    write_port_file(port)
    if mode == "attach":
        print(f"AgentForge engine already up {_ui_url(host, port)}", flush=True)
        release_lock()
        return 0
    if mode == "busy":
        print(f"ports {preferred}-{preferred + 5} busy and not AgentForge", file=sys.stderr)
        release_lock()
        return 3
    log_line(f"spawn {port}")
    cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", host, "--port", str(port), "--log-level", "info",
    ]
    if reload:
        cmd.append("--reload")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    log_fh = LOG_FILE.open("a", encoding="utf-8")
    proc = subprocess.Popen(cmd, cwd=str(ROOT), env=env, stdout=log_fh, stderr=log_fh)
    write_child(proc.pid)
    try:
        if not wait_healthy(host, port):
            proc.terminate()
            log_line("health timeout")
            return 2
        print(f"AgentForge engine {_ui_url(host, port)}", flush=True)
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        return 0
    finally:
        try:
            log_fh.close()
        except OSError:
            pass
        clear_child()
        release_lock()


def main() -> int:
    parser = argparse.ArgumentParser(prog="launch_engine_min")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--doctor", action="store_true")
    parser.add_argument("--open-ui", action="store_true")
    args = parser.parse_args()
    if args.doctor:
        report = doctor(args.host, args.port)
        for check in report["checks"]:
            mark = "ok" if check["ok"] else "fail"
            print(f"{mark:4} {check['id']:12} {check['detail']}", flush=True)
        print("ready" if report["ready"] else ("install-ok" if report["ok"] else "not-ready"), flush=True)
        return 0 if report["ok"] else 1
    if args.status:
        info = engine_status(args.host, args.port)
        state = "up" if info["healthy"] else "down"
        print(f"{state} {info['ui']} pid={info['pid'] or '-'} lock_stale={info['lock_stale']}", flush=True)
        return 0 if info["healthy"] else 1
    if args.stop:
        return stop_engine(args.host, args.port)
    if args.open_ui:
        info = engine_status(args.host, args.port)
        print(info["ui"], flush=True)
        print("open-ui-ok" if info["healthy"] else "open-ui-fail", flush=True)
        return 0 if info["healthy"] else 2
    return spawn_engine(args.host, args.port, reload=args.reload)


if __name__ == "__main__":
    raise SystemExit(main())
