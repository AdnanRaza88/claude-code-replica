# Restored base runtime (pre F-018) + plan mode hooks + agent_reach tool hints.
from __future__ import annotations

import urllib.request

_URL = (
    "https://raw.githubusercontent.com/AdnanRaza88/claude-code-replica/"
    "46c0ab28cb69095ec7e26af002341331ef511391/src/orchestration/runtime.py"
)

with urllib.request.urlopen(_URL, timeout=60) as _resp:
    _code = _resp.read().decode("utf-8")

# Soft-inject agent_reach / pinchtab guidance into leaf tool_hint if present
_HINT_OLD = (
    "CRITICAL: For news, today's date, current events, Google updates, or any live web fact "
    "you MUST call tool 'web_search' first (then 'web_fetch' on a useful URL). "
)
_HINT_NEW = (
    "CRITICAL: For news, today's date, current events, Google updates, or any live web fact "
    "you MUST call tool 'web_search' first (then 'web_fetch' or 'agent_reach' web_read). "
    "For Wikipedia / YouTube / Reddit prefer tool 'agent_reach'. "
    "For interactive browser pages use 'pinchtab' if available. "
)
if _HINT_OLD in _code:
    _code = _code.replace(_HINT_OLD, _HINT_NEW, 1)
else:
    # Alternate shorter hint shapes from other base versions
    for old, new in [
        (
            "For current public facts use 'web_search' then 'web_fetch'",
            "For current public facts use 'web_search' then 'web_fetch' or 'agent_reach'",
        ),
        (
            "Do NOT invent headlines, dates, or URLs.\n",
            "Do NOT invent headlines, dates, or URLs.\n"
            "For Wikipedia/YouTube/Reddit use tool 'agent_reach'. For live UI use 'pinchtab'.\n",
        ),
    ]:
        if old in _code:
            _code = _code.replace(old, new, 1)
            break

exec(compile(_code, __file__, "exec"), globals())

# F-018 plan mode — install even when app imports runtime module directly
try:
    from src.orchestration import plan_mode_hooks

    plan_mode_hooks.install(AgentRuntime)  # type: ignore[name-defined]
except Exception:
    pass
