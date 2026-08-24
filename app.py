# F-018 app entry — load known-good base, wire Mode + tools without breaking ensure_session.
from __future__ import annotations

import urllib.request

_URL = (
    "https://raw.githubusercontent.com/AdnanRaza88/claude-code-replica/"
    "46c0ab28cb69095ec7e26af002341331ef511391/app.py"
)

with urllib.request.urlopen(_URL, timeout=60) as _resp:
    _code = _resp.read().decode("utf-8")

# --- F-018: Mode selection ---
_code = _code.replace(
    'st.selectbox("Mode", ["agent", "plan"], index=0)',
    'run_mode = st.selectbox("Mode", ["agent", "plan"], index=0, key="run_mode_select")',
)

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

_code = _code.replace(
    '<span class="header-meta">session {session.session_id[:8]} · {provider}/{model}</span>',
    '<span class="header-meta">session {session.session_id[:8]} · {provider}/{model} · {(\"PLAN\" if getattr(session, \"mode\", \"agent\") == \"plan\" else \"AGENT\")}</span>',
)

# --- Safe tool registration: PinchTab + AgentReach (never crash app) ---
_TOOL_MARKER = "tool_reg.register(WebFetchTool())"
if _TOOL_MARKER not in _code:
    raise RuntimeError("app patch: WebFetchTool registration site not found")

_TOOL_INJECT = '''tool_reg.register(WebFetchTool())

        # Optional browser + multi-platform reach (fail soft)
        try:
            from src.tools.pinchtab_tool import PinchTabTool

            def _pt_url():
                return st.session_state.get("credentials", {}).get("pinchtab_url") or "http://127.0.0.1:9867"

            def _pt_token():
                return st.session_state.get("credentials", {}).get("pinchtab_token")

            tool_reg.register(PinchTabTool(get_base_url=_pt_url, get_token=_pt_token))
        except Exception as _e:
            st.session_state["pinchtab_load_error"] = str(_e)[:200]

        try:
            from src.tools.agent_reach_tool import AgentReachTool

            tool_reg.register(AgentReachTool())
        except Exception as _e:
            st.session_state["agent_reach_load_error"] = str(_e)[:200]
'''

_code = _code.replace(_TOOL_MARKER, _TOOL_INJECT, 1)

# --- Optional PinchTab sidebar (after GitHub token block if present, else end of sidebar settings) ---
_SIDEBAR_MARKERS = [
    'st.caption("No GitHub token — github tool will report missing credentials")',
    'st.markdown("### Settings")',
]
_SIDEBAR_INJECT = '''
        st.markdown("---")
        st.caption("Browser (PinchTab) — only needed if local pinchtab server is running")
        pt_url = st.text_input(
            "PinchTab URL",
            value=st.session_state.credentials.get("pinchtab_url", "http://127.0.0.1:9867"),
            help="Default http://127.0.0.1:9867. Start with: pinchtab server",
            key="pinchtab_url_input",
        )
        if pt_url:
            st.session_state.credentials["pinchtab_url"] = pt_url.rstrip("/")
        pt_tok = st.text_input(
            "PinchTab token (optional)",
            type="password",
            value=st.session_state.credentials.get("pinchtab_token", ""),
            key="pinchtab_token_input",
        )
        if pt_tok is not None:
            st.session_state.credentials["pinchtab_token"] = pt_tok
'''

# Prefer inject near GitHub caption; fallback skip if structure unknown (tools still register)
for _m in _SIDEBAR_MARKERS[:1]:
    if _m in _code:
        _code = _code.replace(_m, _m + _SIDEBAR_INJECT, 1)
        break

exec(compile(_code, __file__, "exec"), globals())
