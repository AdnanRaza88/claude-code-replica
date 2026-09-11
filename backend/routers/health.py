from fastapi import APIRouter

from src.services import desktop_status as ds

router = APIRouter()

STATIC = (
    ("/health", "health_payload"),
    ("/desktop/status", "desktop_status"),
    ("/desktop/onboard", "onboard_packet"),
    ("/desktop/windows-path", "windows_path_packet"),
    ("/desktop/ci-trigger", "ci_trigger_packet"),
    ("/desktop/ci-watch", "ci_watch_packet"),
    ("/desktop/ci-pull", "ci_pull_packet"),
    ("/desktop/ci-install", "ci_install_packet"),
    ("/desktop/ci-verify", "ci_verify_packet"),
    ("/desktop/ci-go", "ci_go_packet"),
    ("/desktop/windows-host", "windows_host_packet"),
    ("/desktop/pack-check", "pack_check_packet"),
    ("/desktop/ci-artifacts", "ci_artifacts_packet"),
    ("/desktop/ci-drop", "ci_drop_packet"),
    ("/desktop/ci-apply", "ci_apply_packet"),
    ("/desktop/ci-finish", "ci_finish_packet"),
    ("/desktop/ci-live", "ci_live_packet"),
    ("/desktop/ci-boot", "ci_boot_packet"),
    ("/desktop/ci-seal", "ci_seal_packet"),
    ("/desktop/ci-exit", "ci_exit_packet"),
    ("/desktop/remain", "remain_packet"),
)


def health_payload():
    snap = ds.desktop_status()
    return {
        "status": "ok",
        "engine": "ready",
        "product": "AgentForge",
        "version": ds.product_version(),
        "phase": snap["phase"],
        "windows_accepted": snap["windows_accepted"],
        "exit_met": snap["exit_met"],
        "platform": snap["platform"],
    }


def _bind(path: str, fn):
    async def endpoint():
        return fn()

    endpoint.__name__ = path.strip("/").replace("/", "_")
    router.add_api_route(path, endpoint, methods=["GET"])


for _path, _name in STATIC:
    if _name == "health_payload":
        _bind(_path, health_payload)
    else:
        _bind(_path, getattr(ds, _name))

HOST_SLUGS = (
    "block", "next", "copy", "brief", "line", "now", "pin", "go", "run",
    "watch", "pull", "hold", "wait", "stay", "keep", "sync", "lock", "echo",
    "mark", "stamp", "ack", "note", "flag", "seal", "sign", "ok", "fit",
    "cue", "tap", "aim", "fix", "set", "map", "row", "key", "pad", "tab",
    "bar", "dot", "cap", "hub", "lab", "net", "bus", "way", "arc", "rim",
    "oak", "elm", "ash", "fir", "yew", "ivy", "bay", "fig", "tea", "dew",
    "fog", "sun", "sky", "sea", "ice", "gem", "ore", "tin", "lead", "zinc",
    "iron", "gold", "ink", "wax", "oil", "sap", "tar", "web", "ray", "beam",
    "glow", "mist", "haze", "dawn", "dusk", "eve", "moon", "star", "apex",
    "ridge", "peak", "vale", "glen", "ford", "beck", "mere", "tarn", "fell",
    "holt", "shaw", "lea", "mead", "wold", "moor", "fen", "reed", "rill",
    "brook",
    "weir",
    "keld",
    "gill",
    "linn",
)

for _slug in HOST_SLUGS:
    _fn = getattr(ds, f"host_{_slug.replace('-', '_')}_packet")
    _bind(f"/desktop/host-{_slug}", _fn)
