from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
import uuid


class ContextRef(BaseModel):
    context_id: str
    heading: str
    start_line: int | None = None
    end_line: int | None = None
    domain: str | None = None
    priority: int = 0


class ContextPack(BaseModel):
    pack_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str | None = None
    domain: str
    role_instructions: str = ""
    source_excerpts: list[str] = Field(default_factory=list)
    project_context: str = ""
    skill_ids: list[str] = Field(default_factory=list)
    tool_contracts: list[dict[str, Any]] = Field(default_factory=list)
    output_schema: dict[str, Any] | None = None
    token_estimate: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_prompt_block(self) -> str:
        parts = []
        if self.role_instructions:
            parts.append(self.role_instructions)
        if self.project_context:
            parts.append("## Project context\n" + self.project_context)
        if self.source_excerpts:
            parts.append("## Reference material\n" + "\n\n".join(self.source_excerpts))
        if self.skill_ids:
            parts.append("## Assigned skills\n" + ", ".join(self.skill_ids))
        return "\n\n".join(parts)
