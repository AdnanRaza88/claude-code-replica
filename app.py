# App entry — base from known-good commit, then wire F-018 Mode select.
from __future__ import annotations

import urllib.request

_URL = (
    "https://raw.githubusercontent.com/AdnanRaza88/claude-code-replica/"
    "46c0ab28cb69095ec7e26af002341331ef511391/app.py"
)

with urllib.request.urlopen(_URL, timeout=60) as _resp:
    _code = _resp.read().decode("utf-8")

# F-018: Mode select must set session.mode (plan | agent)
_code = _code.replace(
    'st.selectbox("Mode", ["agent", "plan"], index=0)',
    'run_mode = st.selectbox(\n            "Mode",\n            ["agent", "plan"],\n            index=0,\n            key="run_mode_select",\n            help="plan = read/search/web only, no write/edit/bash. agent = full execution.",\n        )',
)

_code = _code.replace(
    "def ensure_session(services, provider: str, model: str, base_url: str | None, mode: str):",
    "def ensure_session(services, provider: str, model: str, base_url: str | None, permission_mode: str, run_mode: str = \"agent\"):",
)

_code = _code.replace(
    "permission_mode=PermissionMode(mode),\n        project_root=str(Path.cwd()),\n    )",
    "permission_mode=PermissionMode(permission_mode),\n        project_root=str(Path.cwd()),\n        mode=run_mode if run_mode in (\"agent\", \"plan\") else \"agent\",\n    )",
)

_code = _code.replace(
    "session = ensure_session(services, provider, model, base_url.strip() or None, perm_mode)\n    services[\"permission\"].set_mode(PermissionMode(perm_mode))",
    "session = ensure_session(services, provider, model, base_url.strip() or None, perm_mode, run_mode=run_mode)\n    services[\"permission\"].set_mode(PermissionMode(perm_mode))\n    if hasattr(services[\"session\"], \"set_mode\"):\n        services[\"session\"].set_mode(session.session_id, run_mode)",
)

_code = _code.replace(
    '<span class="header-meta">session {session.session_id[:8]} · {provider}/{model}</span>',
    '<span class="header-meta">session {session.session_id[:8]} · {provider}/{model} · {(\"PLAN\" if getattr(session, \"mode\", \"agent\") == \"plan\" else \"AGENT\")}</span>',
)

exec(compile(_code, __file__, "exec"), globals())
