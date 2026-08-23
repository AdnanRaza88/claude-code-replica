from __future__ import annotations

from typing import Callable
from src.models.provider import ProviderConfig
from .base import ModelProvider
from .openai_compatible import OpenAICompatibleProvider
from .ollama import OllamaProvider
from .groq import GroqProvider
from .gemini import GeminiProvider
from .presets import get_preset


class ProviderRegistry:
    def __init__(self):
        self._factories: dict[str, Callable[..., ModelProvider]] = {
            "ollama": lambda cfg, key: OllamaProvider(
                base_url=cfg.base_url or get_preset("ollama")["base_url"],
                api_key=key or "ollama",
            ),
            "groq": lambda cfg, key: GroqProvider(
                api_key=key,
                base_url=cfg.base_url or get_preset("groq")["base_url"],
            ),
            "gemini": lambda cfg, key: GeminiProvider(
                api_key=key,
                base_url=cfg.base_url or get_preset("gemini")["base_url"],
            ),
            "openai": lambda cfg, key: OpenAICompatibleProvider(
                api_key=key,
                base_url=cfg.base_url or get_preset("openai")["base_url"],
            ),
            "opencode": lambda cfg, key: OpenAICompatibleProvider(
                api_key=key,
                base_url=cfg.base_url or get_preset("opencode")["base_url"],
            ),
            "zen": lambda cfg, key: OpenAICompatibleProvider(
                api_key=key,
                base_url=cfg.base_url or get_preset("zen")["base_url"],
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

    def default_base_url(self, provider: str) -> str:
        return get_preset(provider).get("base_url") or ""

    def default_model(self, provider: str) -> str:
        return get_preset(provider).get("default_model") or ""

    def fallback_models(self, provider: str) -> list[str]:
        return list(get_preset(provider).get("models") or [])
