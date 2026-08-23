from __future__ import annotations

from typing import Protocol, runtime_checkable
from src.models.provider import Message, ModelResponse, ToolSpec, ProviderConfig


@runtime_checkable
class ModelProvider(Protocol):
    async def invoke(
        self,
        messages: list[Message],
        *,
        model: str,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> ModelResponse:
        ...

    async def list_models(self) -> list[str]:
        ...
