from __future__ import annotations

from .openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.groq.com/openai/v1"):
        super().__init__(api_key=api_key, base_url=base_url)
