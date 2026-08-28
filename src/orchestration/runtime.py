# Runtime loader — full AgentRuntime from known-good commit + session episode wrap.
from __future__ import annotations

import urllib.request

_URL = (
    "https://raw.githubusercontent.com/AdnanRaza88/claude-code-replica/"
    "46c0ab28cb69095ec7e26af002341331ef511391/src/orchestration/runtime.py"
)

with urllib.request.urlopen(_URL, timeout=60) as _resp:
    _code = _resp.read().decode("utf-8")

_HINT_OLD = (
    "CRITICAL: For news, today's date, current events, Google updates, or any live web fact "
    "you MUST call tool 'web_search' first (then 'web_fetch' on a useful URL). "
)
_HINT_NEW = (
    "CRITICAL: For news, today's date, current events, Google updates, or any live web fact "
    "you MUST call tool 'web_search' first (then 'web_fetch' or 'agent_reach' web_read). "
    "For Wikipedia / YouTube / Reddit prefer tool 'agent_reach'. "
    "For interactive browser pages use 'pinchtab' if available. "
    "For durable facts / session recall use tool 'memory'. "
)
if _HINT_OLD in _code:
    _code = _code.replace(_HINT_OLD, _HINT_NEW, 1)
else:
    for old, new in [
        (
            "For current public facts use 'web_search' then 'web_fetch'",
            "For current public facts use 'web_search' then 'web_fetch' or 'agent_reach'; for memory use 'memory'",
        ),
        (
            "Do NOT invent headlines, dates, or URLs.\n",
            "Do NOT invent headlines, dates, or URLs.\n"
            "For Wikipedia/YouTube/Reddit use 'agent_reach'. For memory use 'memory'.\n",
        ),
    ]:
        if old in _code:
            _code = _code.replace(old, new, 1)
            break

exec(compile(_code, __file__, "exec"), globals())

try:
    from src.orchestration import plan_mode_hooks

    plan_mode_hooks.install(AgentRuntime)  # type: ignore[name-defined]
except Exception:
    pass

try:
    from src.services.session_memory import SessionMemoryService
    from src.models.events import EventType as _ET

    _orig_run = AgentRuntime.run_task  # type: ignore[name-defined]

    async def _run_task_with_episode(self, session_id, objective, project_context=""):
        result = await _orig_run(self, session_id, objective, project_context)
        try:
            session = self.sessions.get(session_id)
            if session is None:
                return result
            events = self.events.list_events(session_id, limit=500)
            files, tools = [], []
            for ev in events:
                if getattr(ev, "event_type", None) == _ET.TOOL_STARTED and ev.message:
                    tools.append(ev.message)
                payload = getattr(ev, "payload", None) or {}
                for key in ("path", "file", "filepath"):
                    if payload.get(key):
                        files.append(str(payload[key]))
                tin = payload.get("tool_input") or {}
                if isinstance(tin, dict):
                    for key in ("path", "file", "filepath"):
                        if tin.get(key):
                            files.append(str(tin[key]))
            summary = ""
            if isinstance(result, dict):
                summary = str(result.get("summary") or result.get("plan") or "")[:600]
            SessionMemoryService(project_root=session.project_root).record(
                objective=objective,
                summary=summary,
                files=files,
                tools=tools,
                mode=getattr(session, "mode", None) or "agent",
                session_id=session_id,
            )
        except Exception:
            pass
        return result

    AgentRuntime.run_task = _run_task_with_episode  # type: ignore[name-defined]
except Exception:
    pass
