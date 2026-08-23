from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
import uuid


class Skill(BaseModel):
    skill_id: str
    name: str
    domain: str
    description: str
    body: str
    allowed_tools: list[str] = Field(default_factory=list)
    priority: int = 50
    version: str = "1.0"
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_prompt_section(self, max_chars: int = 6000) -> str:
        text = self.body.strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[skill truncated]"
        return f"## Skill: {self.name}\n{self.description}\n\n{text}"
