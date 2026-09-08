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
    host_ack_packet,
    host_note_packet,
    host_flag_packet,
    host_seal_packet,
    host_sign_packet,
    host_ok_packet,
    host_fit_packet,
    host_cue_packet,
    host_tap_packet,
    host_aim_packet,
    host_fix_packet,
    host_set_packet,
    host_map_packet,
    host_row_packet,
    host_key_packet,
    host_pad_packet,
    host_tab_packet,
    host_bar_packet,
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


@router.get("/desktop/host-keep")
async def desktop_host_keep():
    return host_keep_packet()


@router.get("/desktop/host-sync")
async def desktop_host_sync():
    return host_sync_packet()


@router.get("/desktop/host-lock")
async def desktop_host_lock():
    return host_lock_packet()


@router.get("/desktop/host-echo")
async def desktop_host_echo():
    return host_echo_packet()


@router.get("/desktop/host-mark")
async def desktop_host_mark():
    return host_mark_packet()


@router.get("/desktop/host-stamp")
async def desktop_host_stamp():
    return host_stamp_packet()


@router.get("/desktop/host-ack")
async def desktop_host_ack():
    return host_ack_packet()


@router.get("/desktop/host-note")
async def desktop_host_note():
    return host_note_packet()


@router.get("/desktop/host-flag")
async def desktop_host_flag():
    return host_flag_packet()


@router.get("/desktop/host-seal")
async def desktop_host_seal():
    return host_seal_packet()


@router.get("/desktop/host-sign")
async def desktop_host_sign():
    return host_sign_packet()


@router.get("/desktop/host-ok")
async def desktop_host_ok():
    return host_ok_packet()


@router.get("/desktop/host-fit")
async def desktop_host_fit():
    return host_fit_packet()


@router.get("/desktop/host-cue")
async def desktop_host_cue():
    return host_cue_packet()


@router.get("/desktop/host-tap")
async def desktop_host_tap():
    return host_tap_packet()


@router.get("/desktop/host-aim")
async def desktop_host_aim():
    return host_aim_packet()


@router.get("/desktop/host-fix")
async def desktop_host_fix():
    return host_fix_packet()


@router.get("/desktop/host-set")
async def desktop_host_set():
    return host_set_packet()


@router.get("/desktop/host-map")
async def desktop_host_map():
    return host_map_packet()


@router.get("/desktop/host-row")
async def desktop_host_row():
    return host_row_packet()


@router.get("/desktop/host-key")
async def desktop_host_key():
    return host_key_packet()


@router.get("/desktop/host-pad")
async def desktop_host_pad():
    return host_pad_packet()


@router.get("/desktop/host-tab")
async def desktop_host_tab():
    return host_tab_packet()


@router.get("/desktop/host-bar")
async def desktop_host_bar():
    return host_bar_packet()
