from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str
    name: str | None = None
    tool_call_id: str | None = None


class ProviderConfig(BaseModel):
    provider: str
    model: str
    base_url: str | None = None
    credential_ref: str | None = None
    temperature: float = 0.2
    max_tokens: int = 4096
    extra: dict[str, Any] = Field(default_factory=dict)


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ModelResponse(BaseModel):
    content: str | None = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    finish_reason: str | None = None
    usage: dict[str, int] = Field(default_factory=dict)
    raw: dict[str, Any] | None = None
