# F-018 app entry — load known-good base, wire Mode without breaking ensure_session.
from __future__ import annotations

import urllib.request

_URL = (
    "https://raw.githubusercontent.com/AdnanRaza88/claude-code-replica/"
    "46c0ab28cb69095ec7e26af002341331ef511391/app.py"
)

with urllib.request.urlopen(_URL, timeout=60) as _resp:
    _code = _resp.read().decode("utf-8")

# Capture Mode selection into run_mode (do not change ensure_session signature)
_code = _code.replace(
    'st.selectbox("Mode", ["agent", "plan"], index=0)',
    'run_mode = st.selectbox("Mode", ["agent", "plan"], index=0, key="run_mode_select")',
)

# After session is ready, set session.mode for plan-mode hooks (no create() signature change)
_old = (
    "session = ensure_session(services, provider, model, base_url.strip() or None, perm_mode)\n"
    "    services[\"permission\"].set_mode(PermissionMode(perm_mode))"
)
_new = (
    "session = ensure_session(services, provider, model, base_url.strip() or None, perm_mode)\n"
    "    services[\"permission\"].set_mode(PermissionMode(perm_mode))\n"
    "    _rm = run_mode if \"run_mode\" in dir() else \"agent\"\n"
    "    if _rm not in (\"agent\", \"plan\"):\n"
    "        _rm = \"agent\"\n"
    "    session.mode = _rm\n"
    "    if hasattr(services[\"session\"], \"set_mode\"):\n"
    "        services[\"session\"].set_mode(session.session_id, _rm)"
)
if _old not in _code:
    raise RuntimeError("F-018 app patch: ensure_session call site not found")
_code = _code.replace(_old, _new)

# Header shows PLAN | AGENT
_code = _code.replace(
    '<span class="header-meta">session {session.session_id[:8]} · {provider}/{model}</span>',
    '<span class="header-meta">session {session.session_id[:8]} · {provider}/{model} · {(\"PLAN\" if getattr(session, \"mode\", \"agent\") == \"plan\" else \"AGENT\")}</span>',
)

exec(compile(_code, __file__, "exec"), globals())
