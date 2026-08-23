from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from .base import Tool, ToolResult


class SearchInput(BaseModel):
    query: str
    path: str = "."
    max_results: int = 30


class ProjectSearchTool(Tool):
    name = "search"
    description = "Search for a pattern across project files"
    risk = "low"
    input_schema = SearchInput

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.cwd()
        self.skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache"}

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = SearchInput(**input_data)
            base = (self.root / data.path).resolve()
            if not str(base).startswith(str(self.root.resolve())):
                return ToolResult(success=False, error="path outside workspace")
            pattern = re.compile(data.query, re.IGNORECASE)
            hits: list[str] = []
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = [d for d in dirnames if d not in self.skip_dirs]
                for name in filenames:
                    if len(hits) >= data.max_results:
                        break
                    fp = Path(dirpath) / name
                    try:
                        text = fp.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        continue
                    for i, line in enumerate(text.splitlines(), start=1):
                        if pattern.search(line):
                            rel = fp.relative_to(self.root)
                            hits.append(f"{rel}:{i}:{line.strip()[:200]}")
                            if len(hits) >= data.max_results:
                                break
            return ToolResult(
                success=True,
                output="\n".join(hits) if hits else "no matches",
                data={"count": len(hits)},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
