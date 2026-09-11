from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


SECRET_FIELDS = (
    "gemini_api_key",
    "opencode_api_key",
    "openai_api_key",
    "groq_api_key",
    "github_token",
    "pinchtab_token",
    "agent_reach_token",
)


class AppSettings(BaseModel):
    gemini_api_key: str = ""
    opencode_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    ollama_base_url: str = "http://127.0.0.1:11434"
    github_token: str = ""
    pinchtab_url: str = "http://127.0.0.1:9867"
    pinchtab_token: str = ""
    agent_reach_base_url: str = ""
    agent_reach_token: str = ""
    engine_host: str = "127.0.0.1"
    engine_port: int = 8787
    workspace: str = ""
    first_run_done: bool = False
    extra: dict[str, Any] = Field(default_factory=dict)


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return value[:3] + "…" + value[-2:]


class SettingsService:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._settings = AppSettings()
        self.load()

    def load(self) -> AppSettings:
        if not self.path.is_file():
            return self._settings
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self._settings = AppSettings.model_validate(raw)
        except (json.JSONDecodeError, OSError, ValueError):
            self._settings = AppSettings()
        return self._settings

    def get(self) -> AppSettings:
        return self._settings.model_copy(deep=True)

    def public_dict(self, reveal: bool = False) -> dict[str, Any]:
        data = self._settings.model_dump()
        if reveal:
            return data
        for key in SECRET_FIELDS:
            if key in data and isinstance(data[key], str):
                data[key] = _mask(data[key])
        data["has_secrets"] = {
            key: bool(getattr(self._settings, key)) for key in SECRET_FIELDS
        }
        return data

    def update(self, patch: dict[str, Any]) -> AppSettings:
        current = self._settings.model_dump()
        extra = current.get("extra") or {}
        incoming_extra = patch.pop("extra", None)
        if isinstance(incoming_extra, dict):
            extra.update(incoming_extra)
        for key, value in patch.items():
            if key not in current:
                extra[key] = value
                continue
            if key in SECRET_FIELDS and isinstance(value, str) and "…" in value:
                continue
            if key in SECRET_FIELDS and value == "****":
                continue
            current[key] = value
        current["extra"] = extra
        self._settings = AppSettings.model_validate(current)
        self.save()
        return self.get()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self._settings.model_dump(), indent=2)
        self.path.write_text(payload, encoding="utf-8")
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def clear(self) -> AppSettings:
        self._settings = AppSettings()
        if self.path.exists():
            self.path.unlink()
        return self.get()


_default: SettingsService | None = None


def default_settings_path(root: Path | None = None) -> Path:
    override = os.environ.get("AGENTFORGE_SETTINGS")
    if override:
        return Path(override)
    base = root or Path.cwd()
    return base / ".agentforge" / "settings.json"


def reset_settings_service() -> None:
    global _default
    _default = None


def get_settings_service(root: Path | None = None) -> SettingsService:
    global _default
    if _default is None:
        _default = SettingsService(default_settings_path(root))
    return _default
