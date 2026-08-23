from __future__ import annotations

from typing import Any, Callable
from src.models.provider import ProviderConfig
from .base import ModelProvider
from .openai_compatible import OpenAICompatibleProvider
from .ollama import OllamaProvider
from .groq import GroqProvider
from .gemini import GeminiProvider


class ProviderRegistry:
    def __init__(self):
        self._factories: dict[str, Callable[..., ModelProvider]] = {
            "ollama": lambda cfg, key: OllamaProvider(
                base_url=cfg.base_url or "http://localhost:11434/v1",
                api_key=key or "ollama",
            ),
            "groq": lambda cfg, key: GroqProvider(api_key=key, base_url=cfg.base_url or "https://api.groq.com/openai/v1"),
            "gemini": lambda cfg, key: GeminiProvider(api_key=key, base_url=cfg.base_url or "https://generativelanguage.googleapis.com/v1beta"),
            "openai": lambda cfg, key: OpenAICompatibleProvider(
                api_key=key,
                base_url=cfg.base_url or "https://api.openai.com/v1",
            ),
            "opencode": lambda cfg, key: OpenAICompatibleProvider(
                api_key=key,
                base_url=cfg.base_url or "http://localhost:3000/v1",
            ),
            "zen": lambda cfg, key: OpenAICompatibleProvider(
                api_key=key,
                base_url=cfg.base_url or "http://localhost:8080/v1",
            ),
            "openai_compatible": lambda cfg, key: OpenAICompatibleProvider(
                api_key=key,
                base_url=cfg.base_url or "https://api.openai.com/v1",
            ),
        }

    def register(self, name: str, factory: Callable[..., ModelProvider]) -> None:
        self._factories[name] = factory

    def create(self, config: ProviderConfig, api_key: str | None = None) -> ModelProvider:
        factory = self._factories.get(config.provider)
        if factory is None:
            factory = self._factories["openai_compatible"]
        return factory(config, api_key)

    def list_providers(self) -> list[str]:
        return sorted(self._factories.keys())
