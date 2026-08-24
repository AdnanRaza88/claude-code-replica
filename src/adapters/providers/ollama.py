from __future__ import annotations

from typing import Any
import httpx

from .openai_compatible import OpenAICompatibleProvider
from src.models.provider import Message, ModelResponse, ToolSpec


class OllamaProvider(OpenAICompatibleProvider):
    """Ollama local/remote. OpenAI /v1 path with native /api fallback."""

    def __init__(self, base_url: str = "http://localhost:11434/v1", api_key: str | None = "ollama"):
        raw = (base_url or "http://localhost:11434/v1").rstrip("/")
        if raw.endswith("/v1"):
            self.native_base = raw[:-3] or raw
            openai_base = raw
        else:
            self.native_base = raw
            openai_base = f"{raw}/v1"
        super().__init__(api_key=api_key or "ollama", base_url=openai_base)
        self.timeout = 180.0

    async def list_models(self) -> list[str]:
        models = await super().list_models()
        if models:
            return models
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{self.native_base}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    names = []
                    for m in data.get("models") or []:
                        name = m.get("name") or m.get("model")
                        if name:
                            names.append(str(name))
                    if names:
                        return sorted(set(names))
        except Exception:
            pass
        return []

    async def ping(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                try:
                    r = await client.get(f"{self.native_base}/api/version")
                    if r.status_code == 200:
                        ver = r.json().get("version", "?")
                        models = await self.list_models()
                        return {
                            "ok": True,
                            "message": f"Ollama reachable (v{ver}) · {len(models)} model(s)",
                            "models": models,
                            "version": ver,
                        }
                except Exception:
                    pass
                r2 = await client.get(f"{self.base_url}/models", headers=self._headers())
                if r2.status_code == 200:
                    models = await self.list_models()
                    return {
                        "ok": True,
                        "message": f"Ollama OpenAI endpoint OK · {len(models)} model(s)",
                        "models": models,
                    }
                return {
                    "ok": False,
                    "message": f"HTTP {r2.status_code} from {self.base_url}/models",
                    "models": [],
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "message": (
                    f"Cannot reach Ollama at {self.native_base}. "
                    "If this app runs on Streamlit Cloud, localhost is the cloud server — not your PC. "
                    "Options: (1) run Streamlit on the same machine as Ollama, "
                    "(2) expose Ollama via ngrok and paste that URL as Base URL."
                ),
                "models": [],
            }
        except Exception as e:
            return {"ok": False, "message": str(e)[:300], "models": []}

    async def invoke(
        self,
        messages: list[Message],
        *,
        model: str,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> ModelResponse:
        try:
            return await super().invoke(
                messages,
                model=model,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as openai_err:
            try:
                payload = {
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                }
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(f"{self.native_base}/api/chat", json=payload)
                    if resp.status_code >= 400:
                        raise RuntimeError(
                            f"Ollama native HTTP {resp.status_code}: {resp.text[:400]}"
                        )
                    data = resp.json()
                content = (data.get("message") or {}).get("content") or data.get("response") or ""
                return ModelResponse(
                    content=content,
                    tool_calls=[],
                    usage={
                        "prompt_tokens": data.get("prompt_eval_count") or 0,
                        "completion_tokens": data.get("eval_count") or 0,
                        "total_tokens": (data.get("prompt_eval_count") or 0)
                        + (data.get("eval_count") or 0),
                    },
                    raw=data,
                )
            except Exception as native_err:
                raise RuntimeError(
                    f"Ollama failed.\nOpenAI path: {openai_err}\nNative path: {native_err}"
                ) from native_err
