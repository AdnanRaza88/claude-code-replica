from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.services.settings_service import get_settings_service

router = APIRouter()


class SettingsPatch(BaseModel):
    model_config = {"extra": "allow"}


@router.get("")
async def read_settings(reveal: bool = Query(default=False)):
    svc = get_settings_service()
    return {"settings": svc.public_dict(reveal=reveal)}


@router.put("")
async def update_settings(patch: SettingsPatch):
    svc = get_settings_service()
    data = patch.model_dump(exclude_unset=True)
    extra = data.pop("extra", None)
    payload: dict[str, Any] = {k: v for k, v in data.items() if v is not None}
    if extra is not None:
        payload["extra"] = extra
    updated = svc.update(payload)
    return {"ok": True, "settings": svc.public_dict(reveal=False), "engine_port": updated.engine_port}


@router.delete("")
async def delete_settings():
    svc = get_settings_service()
    svc.clear()
    return {"ok": True, "settings": svc.public_dict(reveal=False)}
