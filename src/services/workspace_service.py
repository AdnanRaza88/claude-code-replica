"""Project workspace root + artifact ledger for preview/download."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WorkspaceService:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root).expanduser().resolve() if root else Path.cwd().resolve()
        self._artifacts: list[dict[str, Any]] = []

    def set_root(self, root: str | Path) -> Path:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        return self.root

    def resolve(self, rel: str) -> Path:
        path = (self.root / rel).resolve()
        if not str(path).startswith(str(self.root)):
            raise ValueError("path outside workspace")
        return path

    def record(
        self,
        rel_path: str,
        *,
        kind: str = "write",
        nbytes: int = 0,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        entry = {
            "path": rel_path.replace("\\", "/"),
            "kind": kind,
            "bytes": nbytes,
            "agent_id": agent_id,
            "at": datetime.now(timezone.utc).isoformat(),
            "abs": str(self.root / rel_path),
        }
        # de-dupe by path — keep latest
        self._artifacts = [a for a in self._artifacts if a["path"] != entry["path"]]
        self._artifacts.append(entry)
        return entry

    def list_artifacts(self, limit: int = 80) -> list[dict[str, Any]]:
        return list(reversed(self._artifacts[-limit:]))

    def clear_artifacts(self) -> None:
        self._artifacts.clear()

    def read_preview(self, rel_path: str, max_chars: int = 12_000) -> dict[str, Any]:
        try:
            path = self.resolve(rel_path)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        if not path.is_file():
            return {"ok": False, "error": f"not a file: {rel_path}"}
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return {"ok": False, "error": str(e)}
        truncated = len(text) > max_chars
        if truncated:
            text = text[:max_chars] + "\n\n...[truncated]..."
        return {
            "ok": True,
            "path": rel_path,
            "abs": str(path),
            "text": text,
            "truncated": truncated,
            "size": path.stat().st_size,
        }

    def read_bytes(self, rel_path: str) -> bytes | None:
        try:
            path = self.resolve(rel_path)
            if path.is_file():
                return path.read_bytes()
        except (ValueError, OSError):
            return None
        return None

    def scan_specs(self, limit: int = 40) -> list[dict[str, Any]]:
        """List .agentforge/specs files for SDD preview."""
        specs = self.root / ".agentforge" / "specs"
        if not specs.is_dir():
            return []
        out: list[dict[str, Any]] = []
        for path in sorted(specs.rglob("*.md")):
            try:
                rel = str(path.relative_to(self.root)).replace("\\", "/")
                out.append(
                    {
                        "path": rel,
                        "kind": "spec",
                        "bytes": path.stat().st_size,
                        "at": datetime.fromtimestamp(
                            path.stat().st_mtime, tz=timezone.utc
                        ).isoformat(),
                        "abs": str(path),
                    }
                )
            except (OSError, ValueError):
                continue
            if len(out) >= limit:
                break
        return out

    def combined_files(self, limit: int = 60) -> list[dict[str, Any]]:
        seen: set[str] = set()
        merged: list[dict[str, Any]] = []
        for a in self.list_artifacts(limit=limit):
            if a["path"] not in seen:
                seen.add(a["path"])
                merged.append(a)
        for a in self.scan_specs(limit=limit):
            if a["path"] not in seen:
                seen.add(a["path"])
                merged.append(a)
        return merged[:limit]
