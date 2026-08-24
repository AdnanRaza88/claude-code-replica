"""Streamlit helpers: workspace path + artifact preview/download."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def apply_workspace_root(services: dict[str, Any], root: str) -> tuple[bool, str]:
    root = (root or "").strip()
    if not root:
        return False, "empty path"
    path = Path(root).expanduser()
    try:
        path.mkdir(parents=True, exist_ok=True)
        resolved = path.resolve()
    except OSError as e:
        return False, str(e)

    ws = services.get("workspace")
    if ws is not None:
        ws.set_root(resolved)

    tools = services.get("tools")
    if tools is not None:
        for name in ("read", "write", "edit", "search", "bash"):
            t = tools.get(name) if hasattr(tools, "get") else None
            if t is not None and hasattr(t, "set_root"):
                t.set_root(resolved)
            elif t is not None and hasattr(t, "root"):
                t.root = resolved

    ctx = services.get("context")
    if ctx is not None and hasattr(ctx, "set_project_root"):
        ctx.set_project_root(resolved)

    return True, str(resolved)


def render_artifacts_panel(st, services: dict[str, Any]) -> None:
    ws = services.get("workspace")
    st.markdown('<div class="section-label">Artifacts</div>', unsafe_allow_html=True)
    st.caption("Files agents wrote/edited + .agentforge/specs — preview & download")

    if ws is None:
        st.caption("Workspace service not available")
        return

    files = ws.combined_files(limit=50)
    if not files:
        st.caption("No artifacts yet — run a task that writes files or specs")
        return

    labels = [f"{f['path']} ({f.get('kind', '?')})" for f in files]
    idx = st.selectbox(
        "File",
        range(len(labels)),
        format_func=lambda i: labels[i],
        key="artifact_select",
    )
    chosen = files[idx]
    rel = chosen["path"]
    preview = ws.read_preview(rel)
    if not preview.get("ok"):
        st.warning(preview.get("error") or "cannot read")
        return

    st.caption(f"{preview.get('abs', rel)} · {preview.get('size', 0)} bytes")
    text = preview.get("text") or ""
    lang = "markdown" if rel.endswith(".md") else "python" if rel.endswith(".py") else "text"
    st.code(text, language=lang)

    raw = ws.read_bytes(rel)
    if raw is not None:
        st.download_button(
            label="Download",
            data=raw,
            file_name=Path(rel).name,
            mime="text/plain",
            key=f"dl_{rel}",
            use_container_width=True,
        )
