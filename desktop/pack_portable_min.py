from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ESSENTIAL = (
    "backend",
    "frontend",
    "src",
    "skills",
    "requirements.txt",
    "STRUCTURE.md",
    "desktop/VERSION",
    "desktop/launch_engine_min.py",
    "desktop/windows/Start-AgentForge.bat",
    "desktop/windows/Wait-And-Open.ps1",
    "desktop/windows/Resolve-Python.ps1",
    "desktop/windows/Open-UI-AgentForge.bat",
    "desktop/windows/Stop-AgentForge.bat",
    "desktop/windows/Doctor-AgentForge.bat",
)


def read_version() -> str:
    path = ROOT / "desktop" / "VERSION"
    if not path.is_file():
        return "0.0.0"
    return path.read_text(encoding="utf-8").strip() or "0.0.0"


def _copy_item(src: Path, dest_root: Path) -> bool:
    if not src.exists():
        return False
    rel = src.relative_to(ROOT)
    target = dest_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
    else:
        shutil.copy2(src, target)
    return True


def layout_pack(dest: Path) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    missing: list[str] = []
    for item in ESSENTIAL:
        src = ROOT / item
        if _copy_item(src, dest):
            copied.append(item)
        else:
            missing.append(item)
    readme = dest / "README-PORTABLE.txt"
    readme.write_text(
        "AgentForge portable (min)\n"
        f"version {read_version()}\n"
        "Start: python desktop/launch_engine_min.py\n"
        "Then open /ui/\n",
        encoding="utf-8",
    )
    return {
        "ok": not missing,
        "dest": str(dest),
        "copied": copied,
        "missing": missing,
        "version": read_version(),
    }


def zip_pack(dest: Path, zip_path: Path) -> dict:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in dest.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(dest))
    return {
        "ok": zip_path.is_file(),
        "zip": str(zip_path),
        "bytes": zip_path.stat().st_size if zip_path.is_file() else 0,
    }


def clear_pack(dest: Path) -> bool:
    if dest.exists():
        shutil.rmtree(dest)
    return not dest.exists()


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentForge slim portable pack")
    parser.add_argument("--dest", default=str(ROOT / "dist" / "agentforge-portable-min"))
    parser.add_argument("--zip", default="")
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()
    dest = Path(args.dest)
    if args.clear:
        print("cleared" if clear_pack(dest) else "clear-failed")
        return 0
    report = layout_pack(dest)
    print(report["version"], "copied", len(report["copied"]), "missing", len(report["missing"]))
    if args.zip:
        z = zip_pack(dest, Path(args.zip))
        print("zip", z["bytes"], z["zip"])
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
