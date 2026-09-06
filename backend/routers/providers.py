from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.engine import get_engine
from src.adapters.providers.presets import PROVIDER_PRESETS, annotate_models, model_tier
from src.models.provider import ProviderConfig

router = APIRouter()


class ModelsRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None


@router.get("")
async def list_providers():
    engine = get_engine()
    names = engine.providers.list_providers()
    items = []
    for name in names:
        preset = PROVIDER_PRESETS.get(name, {})
        raw_models = engine.providers.fallback_models(name)
        items.append(
            {
                "id": name,
                "label": preset.get("label", name),
                "default_model": engine.providers.default_model(name),
                "base_url": engine.providers.default_base_url(name),
                "models": raw_models,
                "model_catalog": annotate_models(raw_models),
                "free_models": [m for m in raw_models if model_tier(m) == "free"],
                "needs_key": preset.get("needs_key", True),
            }
        )
    return {"providers": items}


@router.post("/models")
async def live_models(body: ModelsRequest):
    engine = get_engine()
    cfg = ProviderConfig(
        provider=body.provider,
        model=engine.providers.default_model(body.provider) or "default",
        base_url=body.base_url or engine.providers.default_base_url(body.provider) or None,
    )
    client = engine.providers.create(cfg, api_key=body.api_key)
    live: list[str] = []
    error = None
    try:
        live = await client.list_models()
    except Exception as exc:
        error = str(exc)
    fallback = engine.providers.fallback_models(body.provider)
    models = live or fallback
    return {
        "provider": body.provider,
        "models": models,
        "model_catalog": annotate_models(models),
        "free_models": [m for m in models if model_tier(m) == "free"],
        "live": bool(live),
        "error": error,
    }
