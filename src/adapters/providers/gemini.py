from __future__ import annotations

import json
from typing import Any
import httpx

from src.models.provider import Message, ModelResponse, ToolSpec


class GeminiProvider:
    def __init__(self, api_key: str | None = None, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = 90.0

    async def invoke(
        self,
        messages: list[Message],
        *,
        model: str,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> ModelResponse:
        contents = []
        system_parts = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            elif m.role == "assistant":
                contents.append({"role": "model", "parts": [{"text": m.content or ""}]})
            else:
                contents.append({"role": "user", "parts": [{"text": m.content or ""}]})

        body: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_parts:
            body["systemInstruction"] = {"parts": [{"text": "\n".join(system_parts)}]}

        url = f"{self.base_url}/models/{model}:generateContent"
        params = {"key": self.api_key} if self.api_key else {}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, params=params, json=body)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates") or []
        text = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
        usage_meta = data.get("usageMetadata") or {}
        return ModelResponse(
            content=text,
            tool_calls=[],
            finish_reason="stop",
            usage={
                "prompt_tokens": usage_meta.get("promptTokenCount", 0),
                "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
                "total_tokens": usage_meta.get("totalTokenCount", 0),
            },
            raw=data,
        )

    async def list_models(self) -> list[str]:
        params = {"key": self.api_key} if self.api_key else {}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/models", params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            names = []
            for m in data.get("models", []):
                name = m.get("name", "")
                if name.startswith("models/"):
                    name = name[len("models/") :]
                names.append(name)
            return names
