from __future__ import annotations

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from .base import Tool, ToolResult


class ReadInput(BaseModel):
    path: str
    offset: int = 1
    limit: int = 2000


class WriteInput(BaseModel):
    path: str
    content: str


class EditInput(BaseModel):
    path: str
    old_string: str
    new_string: str
    replace_all: bool = False


def _safe_path(root: Path, rel: str) -> Path | None:
    path = (root / rel).resolve()
    if not str(path).startswith(str(root.resolve())):
        return None
    return path


class ReadTool(Tool):
    name = "read"
    description = "Read a file from the project workspace"
    risk = "low"
    input_schema = ReadInput

    def __init__(self, root: str | Path | None = None, workspace=None):
        self.root = Path(root) if root else Path.cwd()
        self.workspace = workspace

    def set_root(self, root: str | Path) -> None:
        self.root = Path(root)

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = ReadInput(**input_data)
            root = Path(self.workspace.root) if self.workspace else self.root
            path = _safe_path(root, data.path)
            if path is None:
                return ToolResult(success=False, error="path outside workspace")
            if not path.exists():
                return ToolResult(success=False, error=f"file not found: {data.path}")
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            start = max(0, data.offset - 1)
            end = start + data.limit
            chunk = lines[start:end]
            numbered = "\n".join(f"{i + start + 1}|{line}" for i, line in enumerate(chunk))
            return ToolResult(
                success=True,
                output=numbered,
                data={"path": data.path, "abs_path": str(path), "total_lines": len(lines)},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class WriteTool(Tool):
    name = "write"
    description = "Write content to a file in the project workspace"
    risk = "high"
    input_schema = WriteInput

    def __init__(self, root: str | Path | None = None, workspace=None):
        self.root = Path(root) if root else Path.cwd()
        self.workspace = workspace

    def set_root(self, root: str | Path) -> None:
        self.root = Path(root)

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = WriteInput(**input_data)
            root = Path(self.workspace.root) if self.workspace else self.root
            path = _safe_path(root, data.path)
            if path is None:
                return ToolResult(success=False, error="path outside workspace")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data.content, encoding="utf-8")
            rel = data.path.replace("\\", "/")
            if self.workspace is not None:
                self.workspace.record(rel, kind="write", nbytes=len(data.content))
            return ToolResult(
                success=True,
                output=f"wrote {len(data.content)} bytes to {data.path}",
                data={
                    "path": rel,
                    "abs_path": str(path),
                    "bytes": len(data.content),
                    "kind": "write",
                    "artifact": True,
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class EditTool(Tool):
    name = "edit"
    description = "Replace text in an existing file"
    risk = "high"
    input_schema = EditInput

    def __init__(self, root: str | Path | None = None, workspace=None):
        self.root = Path(root) if root else Path.cwd()
        self.workspace = workspace

    def set_root(self, root: str | Path) -> None:
        self.root = Path(root)

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = EditInput(**input_data)
            root = Path(self.workspace.root) if self.workspace else self.root
            path = _safe_path(root, data.path)
            if path is None:
                return ToolResult(success=False, error="path outside workspace")
            if not path.exists():
                return ToolResult(success=False, error=f"file not found: {data.path}")
            text = path.read_text(encoding="utf-8")
            if data.old_string not in text:
                return ToolResult(success=False, error="old_string not found")
            if data.replace_all:
                new_text = text.replace(data.old_string, data.new_string)
            else:
                new_text = text.replace(data.old_string, data.new_string, 1)
            path.write_text(new_text, encoding="utf-8")
            rel = data.path.replace("\\", "/")
            if self.workspace is not None:
                self.workspace.record(rel, kind="edit", nbytes=len(new_text))
            return ToolResult(
                success=True,
                output=f"edited {data.path}",
                data={
                    "path": rel,
                    "abs_path": str(path),
                    "bytes": len(new_text),
                    "kind": "edit",
                    "artifact": True,
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
