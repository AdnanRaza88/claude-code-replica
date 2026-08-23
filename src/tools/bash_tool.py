from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from .base import Tool, ToolResult


class BashInput(BaseModel):
    command: str
    timeout: int = 30
    cwd: str | None = None


class BashTool(Tool):
    name = "bash"
    description = "Run a shell command in the project workspace"
    risk = "high"
    input_schema = BashInput

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.cwd()
        self.blocked = {"rm -rf /", "mkfs", "dd if=", ":(){", "shutdown", "reboot"}

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = BashInput(**input_data)
            cmd = data.command.strip()
            for b in self.blocked:
                if b in cmd:
                    return ToolResult(success=False, error="command blocked by policy")
            cwd = self.root
            if data.cwd:
                cwd = (self.root / data.cwd).resolve()
                if not str(cwd).startswith(str(self.root.resolve())):
                    return ToolResult(success=False, error="cwd outside workspace")
            proc = await asyncio.create_subprocess_shell(
                cmd,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=data.timeout)
            except asyncio.TimeoutError:
                proc.kill()
                return ToolResult(success=False, error=f"timed out after {data.timeout}s")
            out = stdout.decode("utf-8", errors="replace")
            err = stderr.decode("utf-8", errors="replace")
            combined = out
            if err:
                combined = (out + "\n" + err).strip()
            return ToolResult(
                success=proc.returncode == 0,
                output=combined[-12000:],
                data={"returncode": proc.returncode},
                error=None if proc.returncode == 0 else f"exit {proc.returncode}",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
