from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SessionMemoryService:
    """Progressive session recall (auto-memory style) over our own runs.

    Stores compact episodes under {project_root}/.agentforge/session_memory/
    so agents can list recent work and files without re-exploring the repo.
    """

    def __init__(self, project_root: str | Path | None = None):
        if project_root:
            self.root = Path(project_root) / ".agentforge" / "session_memory"
        else:
            self.root = Path.home() / ".agentforge" / "session_memory" / "default"
        self.episodes_path = self.root / "episodes.jsonl"

    def _ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.episodes_path.exists():
            self.episodes_path.write_text("", encoding="utf-8")

    def record(
        self,
        *,
        objective: str,
        summary: str = "",
        files: list[str] | None = None,
        tools: list[str] | None = None,
        mode: str = "agent",
        session_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._ensure()
        ep = {
            "id": str(uuid.uuid4())[:12],
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id or "",
            "mode": mode,
            "objective": (objective or "").strip()[:400],
            "summary": (summary or "").strip()[:600],
            "files": list(dict.fromkeys(files or []))[:40],
            "tools": list(dict.fromkeys(tools or []))[:30],
        }
        if extra:
            ep["extra"] = extra
        with open(self.episodes_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ep, ensure_ascii=False) + "\n")
        return ep

    def _load(self) -> list[dict[str, Any]]:
        if not self.episodes_path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line in self.episodes_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def list_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        eps = self._load()
        return list(reversed(eps[-limit:]))

    def files_recent(self, limit: int = 20) -> list[str]:
        seen: list[str] = []
        for ep in reversed(self._load()):
            for p in ep.get("files") or []:
                if p not in seen:
                    seen.append(p)
                    if len(seen) >= limit:
                        return seen
        return seen

    def recall(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        q = (query or "").strip().lower()
        if not q:
            return self.list_recent(limit)
        tokens = [t for t in re.findall(r"[a-z0-9_\-./]{2,}", q) if t]
        scored: list[tuple[float, dict[str, Any]]] = []
        for ep in self._load():
            blob = " ".join(
                [
                    ep.get("objective") or "",
                    ep.get("summary") or "",
                    " ".join(ep.get("files") or []),
                    " ".join(ep.get("tools") or []),
                ]
            ).lower()
            score = 0.0
            for t in tokens:
                if t in blob:
                    score += 1.0 + blob.count(t) * 0.1
            if score > 0:
                scored.append((score, ep))
        scored.sort(key=lambda x: -x[0])
        return [e for _, e in scored[:limit]]

    def wake_block(self, limit: int = 5) -> str:
        eps = self.list_recent(limit)
        if not eps:
            return ""
        lines = [f"## Recent sessions ({len(eps)})"]
        for i, ep in enumerate(eps, 1):
            ts = (ep.get("ts") or "")[:16].replace("T", " ")
            obj = (ep.get("objective") or "")[:80]
            summ = (ep.get("summary") or "")[:100]
            files = ep.get("files") or []
            file_bit = f" | files: {', '.join(files[:4])}" if files else ""
            lines.append(f"{i}. [{ts}] {obj}")
            if summ:
                lines.append(f"   → {summ}{file_bit}")
            elif file_bit:
                lines.append(f"   →{file_bit}")
        return "\n".join(lines)

    def format_list(self, limit: int = 10) -> str:
        eps = self.list_recent(limit)
        if not eps:
            return "No session episodes yet."
        lines = ["#  Date       Objective / summary"]
        for i, ep in enumerate(eps, 1):
            ts = (ep.get("ts") or "")[:16].replace("T", " ")
            obj = (ep.get("objective") or "")[:60]
            summ = (ep.get("summary") or "")[:80]
            lines.append(f"{i:>2}  {ts}  {obj}")
            if summ:
                lines.append(f"      {summ}")
        return "\n".join(lines)

    def format_files(self, limit: int = 20) -> str:
        files = self.files_recent(limit)
        if not files:
            return "No files recorded in recent sessions."
        return "Recent files:\n" + "\n".join(f"- {p}" for p in files)
