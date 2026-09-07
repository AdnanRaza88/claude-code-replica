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
    host_keep_packet,
    host_sync_packet,
    host_lock_packet,
    host_echo_packet,
    host_mark_packet,
    host_stamp_packet,
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
