# Restored base runtime (pre F-018) + plan mode via plan_mode_hooks on import.
# Loads known-good source so Streamlit Cloud does not depend on truncated blobs.
from __future__ import annotations

import urllib.request

_URL = (
    "https://raw.githubusercontent.com/AdnanRaza88/claude-code-replica/"
    "46c0ab28cb69095ec7e26af002341331ef511391/src/orchestration/runtime.py"
)

with urllib.request.urlopen(_URL, timeout=60) as _resp:
    _code = _resp.read().decode("utf-8")

exec(compile(_code, __file__, "exec"), globals())
