from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field
import uuid


class ToolResult(BaseModel):
    success: bool
    output: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    tool_call_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class Tool(ABC):
    name: str
    description: str
    risk: str = "medium"
    input_schema: type[BaseModel] | None = None

    @abstractmethod
    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        ...

    def schema(self) -> dict[str, Any]:
        if self.input_schema is None:
            return {"type": "object", "properties": {}}
        return self.input_schema.model_json_schema()


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def specs_for(self, names: list[str] | None = None) -> list[dict[str, Any]]:
        tools = self.list_tools() if names is None else [self._tools[n] for n in names if n in self._tools]
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.schema(),
                "risk": t.risk,
            }
            for t in tools
        ]
