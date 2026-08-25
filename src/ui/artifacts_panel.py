"""Streamlit helpers: workspace grant + artifact preview/download.

Streamlit cannot open a native OS folder dialog. UX is: agents do not run
until the user explicitly grants a workspace path (existing or newly created).
Native click-to-pick belongs on desktop (Tauri) later.
"""
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


def grant_workspace(services: dict[str, Any], root: str, st_state) -> tuple[bool, str]:
    ok, msg = apply_workspace_root(services, root)
    if not ok:
        return False, msg
    st_state["workspace_root"] = msg
    st_state["workspace_granted"] = True
    sid = st_state.get("active_session_id")
    if sid and services.get("session") and hasattr(services["session"], "set_project_root"):
        services["session"].set_project_root(sid, msg)
    return True, msg


def render_workspace_gate(st, services: dict[str, Any]) -> bool:
    """Full-page gate until user grants workspace. Returns True if granted."""
    if st.session_state.get("workspace_granted") and st.session_state.get("workspace_root"):
        return True

    st.markdown("### Workspace required")
    st.info(
        "Agents need a folder for specs, code, and documents. "
        "Grant a workspace **before** any task runs.\n\n"
        "**Local:** paste your project path, or create a new folder under a parent path.\n"
        "**Streamlit Cloud:** use a path under the deployed app (repo mount). "
        "Native OS folder picker needs the future desktop app — browsers cannot open full disk access."
    )

    tab_use, tab_new = st.tabs(["Use existing folder", "Create new folder"])

    with tab_use:
        existing = st.text_input(
            "Folder path",
            value=st.session_state.get("workspace_path_draft", ""),
            placeholder=r"C:\Users\You\projects\my-app   or   /home/you/projects/my-app",
            key="ws_existing_path",
        )
        if st.button("Grant this workspace", type="primary", key="ws_grant_existing", use_container_width=True):
            ok, msg = grant_workspace(services, existing, st.session_state)
            if ok:
                st.success(f"Workspace granted: {msg}")
                st.rerun()
            else:
                st.error(msg)

    with tab_new:
        parent = st.text_input(
            "Parent directory",
            value=str(Path.home()),
            key="ws_parent_path",
        )
        name = st.text_input("New folder name", value="agent-workspace", key="ws_new_name")
        if st.button("Create & grant", type="primary", key="ws_grant_new", use_container_width=True):
            if not name.strip():
                st.error("Folder name required")
            else:
                target = str(Path(parent).expanduser() / name.strip())
                ok, msg = grant_workspace(services, target, st.session_state)
                if ok:
                    st.success(f"Created & granted: {msg}")
                    st.rerun()
                else:
                    st.error(msg)

    return False


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
