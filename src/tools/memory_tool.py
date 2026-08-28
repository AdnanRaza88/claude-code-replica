from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.tools.base import Tool, ToolResult
from src.services.optmem_service import OptMemStore
from src.services.session_memory import SessionMemoryService


class MemoryInput(BaseModel):
    action: str = Field(
        description=(
            "One of: wake, note, nap, recall, zoom, forget, init, "
            "session_list, session_files, session_recall"
        )
    )
    text: str = Field(default="", description="Note body or nap summary")
    pattern: str = Field(default="", description="Regex for recall")
    lo: int = Field(default=0, description="Range start (inclusive)")
    hi: int = Field(default=0, description="Range end (exclusive for internal; use inclusive end in text)")
    range: str = Field(default="", description="Range as 'lo-hi' inclusive, e.g. 0-1")


def _parse_range(range_str: str, lo: int, hi: int) -> tuple[int, int]:
    if range_str and "-" in range_str:
        a, b = range_str.split("-", 1)
        try:
            return int(a.strip()), int(b.strip()) + 1
        except ValueError:
            pass
    if hi > lo:
        return lo, hi
    if hi == lo and (lo or hi):
        return lo, lo + 1
    return lo, hi


class MemoryTool(Tool):
    name = "memory"
    description = (
        "Agent memory: durable facts (OptMem) + progressive session recall (auto-memory). "
        "wake=durable + recent sessions; note/nap/recall/zoom/forget=durable log; "
        "session_list / session_files / session_recall=recent work without re-exploring; init=create store."
    )
    risk = "low"
    input_schema = MemoryInput

    def __init__(self, project_root: str | None = None):
        self.project_root = project_root

    def _project_root(self, runtime: Any = None) -> str | None:
        root = self.project_root
        if runtime is not None:
            session = getattr(runtime, "sessions", None)
            if session is not None:
                sid = getattr(runtime, "_current_session_id", None)
                if sid:
                    st = session.get(sid)
                    if st and st.project_root:
                        root = st.project_root
        return root

    def _store(self, runtime: Any = None) -> OptMemStore:
        return OptMemStore(project_root=self._project_root(runtime))

    def _sessions(self, runtime: Any = None) -> SessionMemoryService:
        return SessionMemoryService(project_root=self._project_root(runtime))

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        action = (input_data.get("action") or "").strip().lower()
        store = self._store(runtime)
        try:
            if action == "init":
                msg = store.init()
                return ToolResult(success=True, output=msg, data={"path": str(store.root)})

            if action == "wake":
                parts = [store.wake()]
                sess_block = self._sessions(runtime).wake_block(5)
                if sess_block:
                    parts.append(sess_block)
                out = "\n\n".join(parts)
                return ToolResult(success=True, output=out, data={"count": store.count()})

            if action == "session_list":
                out = self._sessions(runtime).format_list(int(input_data.get("lo") or 10) or 10)
                return ToolResult(success=True, output=out)

            if action == "session_files":
                out = self._sessions(runtime).format_files(int(input_data.get("lo") or 20) or 20)
                return ToolResult(success=True, output=out)

            if action == "session_recall":
                q = (input_data.get("pattern") or input_data.get("text") or "").strip()
                hits = self._sessions(runtime).recall(q, limit=8)
                if not hits:
                    return ToolResult(success=True, output="No matching sessions.")
                lines = [f"Session recall for '{q or 'recent'}':"]
                for ep in hits:
                    lines.append(f"- [{(ep.get('ts') or '')[:16]}] {ep.get('objective', '')[:100]}")
                    if ep.get("summary"):
                        lines.append(f"  {ep['summary'][:120]}")
                    if ep.get("files"):
                        lines.append(f"  files: {', '.join(ep['files'][:6])}")
                return ToolResult(success=True, output="\n".join(lines), data={"hits": len(hits)})

            if action == "note":
                text = (input_data.get("text") or "").strip()
                if not text:
                    return ToolResult(success=False, output="", error="note requires text")
                result = store.note(text)
                lines = [f"Recorded #{result['index']}: {result['text']}"]
                if result.get("nap_hint"):
                    lines.append(result["nap_hint"])
                return ToolResult(success=True, output="\n".join(lines), data=result)

            if action == "nap":
                lo, hi = _parse_range(
                    input_data.get("range") or "",
                    int(input_data.get("lo") or 0),
                    int(input_data.get("hi") or 0),
                )
                summary = (input_data.get("text") or "").strip()
                if not summary:
                    return ToolResult(success=False, output="", error="nap requires text summary")
                result = store.nap(lo, hi, summary)
                if result.get("error"):
                    return ToolResult(success=False, output="", error=result["error"])
                return ToolResult(
                    success=True,
                    output=f"Compressed #{result['range']}: {result['summary']}",
                    data=result,
                )

            if action == "recall":
                pattern = (input_data.get("pattern") or input_data.get("text") or "").strip()
                if not pattern:
                    return ToolResult(success=False, output="", error="recall requires pattern")
                out = store.recall(pattern)
                return ToolResult(success=True, output=out)

            if action == "zoom":
                lo, hi = _parse_range(
                    input_data.get("range") or "",
                    int(input_data.get("lo") or 0),
                    int(input_data.get("hi") or 0),
                )
                if hi <= lo:
                    return ToolResult(success=False, output="", error="zoom requires range lo-hi")
                out = store.zoom(lo, hi)
                return ToolResult(success=True, output=out)

            if action == "forget":
                lo, hi = _parse_range(
                    input_data.get("range") or "",
                    int(input_data.get("lo") or 0),
                    int(input_data.get("hi") or 0),
                )
                if hi <= lo:
                    return ToolResult(success=False, output="", error="forget requires range lo-hi")
                out = store.forget(lo, hi)
                return ToolResult(success=True, output=out)

            return ToolResult(
                success=False,
                output="",
                error=(
                    f"unknown action '{action}'. Use: wake, note, nap, recall, zoom, forget, init, "
                    "session_list, session_files, session_recall"
                ),
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e)[:400])
