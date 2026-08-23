from __future__ import annotations

from .openai_compatible import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    def __init__(self, base_url: str = "http://localhost:11434/v1", api_key: str | None = "ollama"):
        super().__init__(api_key=api_key or "ollama", base_url=base_url)
