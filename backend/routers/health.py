from fastapi import APIRouter

from src.services.desktop_status import (
    ci_go_packet,
    ci_install_packet,
    ci_verify_packet,
    ci_pull_packet,
    ci_trigger_packet,
    ci_watch_packet,
    desktop_status,
    onboard_packet,
    product_version,
    pack_check_packet,
    ci_artifacts_packet,
    ci_drop_packet,
    ci_apply_packet,
    ci_finish_packet,
    ci_live_packet,
    ci_boot_packet,
    ci_seal_packet,
    ci_exit_packet,
    remain_packet,
    host_block_packet,
    host_next_packet,
    host_copy_packet,
    host_brief_packet,
    host_line_packet,
    host_now_packet,
    host_pin_packet,
    host_go_packet,
    host_run_packet,
    host_watch_packet,
    host_pull_packet,
    host_hold_packet,
    host_wait_packet,
    host_stay_packet,
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


@router.get("/desktop/onboard")
async def desktop_onboard():
    return onboard_packet()


@router.get("/desktop/windows-path")
async def desktop_windows_path():
    return windows_path_packet()


@router.get("/desktop/ci-trigger")
async def desktop_ci_trigger():
    return ci_trigger_packet()


@router.get("/desktop/ci-watch")
async def desktop_ci_watch():
    return ci_watch_packet()


@router.get("/desktop/ci-pull")
async def desktop_ci_pull():
    return ci_pull_packet()


@router.get("/desktop/ci-install")
async def desktop_ci_install():
    return ci_install_packet()


@router.get("/desktop/ci-verify")
async def desktop_ci_verify():
    return ci_verify_packet()


@router.get("/desktop/ci-go")
async def desktop_ci_go():
    return ci_go_packet()


@router.get("/desktop/windows-host")
async def desktop_windows_host():
    return windows_host_packet()


@router.get("/desktop/pack-check")
async def desktop_pack_check():
    return pack_check_packet()


@router.get("/desktop/ci-artifacts")
async def desktop_ci_artifacts():
    return ci_artifacts_packet()


@router.get("/desktop/ci-drop")
async def desktop_ci_drop():
    return ci_drop_packet()


@router.get("/desktop/ci-apply")
async def desktop_ci_apply():
    return ci_apply_packet()


@router.get("/desktop/ci-finish")
async def desktop_ci_finish():
    return ci_finish_packet()


@router.get("/desktop/ci-live")
async def desktop_ci_live():
    return ci_live_packet()


@router.get("/desktop/ci-boot")
async def desktop_ci_boot():
    return ci_boot_packet()


@router.get("/desktop/ci-seal")
async def desktop_ci_seal():
    return ci_seal_packet()


@router.get("/desktop/ci-exit")
async def desktop_ci_exit():
    return ci_exit_packet()


@router.get("/desktop/remain")
async def desktop_remain():
    return remain_packet()


@router.get("/desktop/host-block")
async def desktop_host_block():
    return host_block_packet()


@router.get("/desktop/host-next")
async def desktop_host_next():
    return host_next_packet()


@router.get("/desktop/host-copy")
async def desktop_host_copy():
    return host_copy_packet()


@router.get("/desktop/host-brief")
async def desktop_host_brief():
    return host_brief_packet()


@router.get("/desktop/host-line")
async def desktop_host_line():
    return host_line_packet()


@router.get("/desktop/host-now")
async def desktop_host_now():
    return host_now_packet()


@router.get("/desktop/host-pin")
async def desktop_host_pin():
    return host_pin_packet()


@router.get("/desktop/host-go")
async def desktop_host_go():
    return host_go_packet()


@router.get("/desktop/host-run")
async def desktop_host_run():
    return host_run_packet()


@router.get("/desktop/host-watch")
async def desktop_host_watch():
    return host_watch_packet()


@router.get("/desktop/host-pull")
async def desktop_host_pull():
    return host_pull_packet()


@router.get("/desktop/host-hold")
async def desktop_host_hold():
    return host_hold_packet()


@router.get("/desktop/host-wait")
async def desktop_host_wait():
    return host_wait_packet()


@router.get("/desktop/host-stay")
async def desktop_host_stay():
    return host_stay_packet()
