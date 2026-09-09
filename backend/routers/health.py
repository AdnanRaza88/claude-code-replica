from fastapi import APIRouter

from src.services.desktop_status import (
    desktop_status,
    product_version,
    host_ore_packet,
    host_tin_packet,
    windows_host_packet,
    windows_path_packet,
)

router = APIRouter()


@router.get("/health")
async def health():
    snap = desktop_status()
    return {
        "status": "ok",
        "engine": "ready",
        "product": "AgentForge",
        "version": product_version(),
        "phase": snap["phase"],
        "windows_accepted": snap["windows_accepted"],
        "exit_met": snap["exit_met"],
        "platform": snap["platform"],
    }


@router.get("/desktop/status")
async def desktop():
    return desktop_status()


@router.get("/desktop/host-ore")
async def desktop_host_ore():
    return host_ore_packet()


@router.get("/desktop/host-tin")
async def desktop_host_tin():
    return host_tin_packet()
