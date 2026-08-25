# Claude Code Replica — Streamlit adapter (workspace + artifacts + F-018 mode)
from __future__ import annotations

import asyncio
from pathlib import Path

import streamlit as st

from src.models.provider import ProviderConfig
from src.models.permission import PermissionMode, PermissionDecision
from src.services.session_service import SessionService
from src.services.permission_service import PermissionService
from src.services.event_service import EventService
from src.services.context_service import ContextService
from src.services.skill_service import SkillService
from src.services.workspace_service import WorkspaceService
from src.adapters.providers.registry import ProviderRegistry
from src.adapters.providers.presets import get_preset, PROVIDER_PRESETS
from src.tools.base import ToolRegistry
from src.tools.file_tools import ReadTool, WriteTool, EditTool
from src.tools.search_tools import ProjectSearchTool
from src.tools.bash_tool import BashTool
from src.tools.github_tool import GitHubTool
from src.tools.web_tools import WebSearchTool, WebFetchTool
from src.orchestration.runtime import AgentRuntime
from src.ui.artifacts_panel import apply_workspace_root, render_artifacts_panel


st.set_page_config(
    page_title="Claude Code Replica",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141820 0%, #0f1117 100%);
        border-right: 1px solid #1e2430;
    }
    div[data-testid="stChatMessage"] {
        border: 1px solid #1e2430;
        border-radius: 10px;
        padding: 0.4rem 0.6rem;
        margin-bottom: 0.5rem;
        background: #161a22;
    }
    .agent-node {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.82rem;
        padding: 0.35rem 0.55rem;
        margin: 0.2rem 0;
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
        background: #161a22;
        color: #c9d1d9;
    }
    .agent-node.succeeded { border-left-color: #22c55e; }
    .agent-node.partial { border-left-color: #eab308; }
    .agent-node.failed { border-left-color: #ef4444; }
    .agent-node.running { border-left-color: #3b82f6; }
    .status-pill {
        display: inline-block;
        font-size: 0.7rem;
        padding: 0.1rem 0.45rem;
        border-radius: 999px;
        font-weight: 600;
    }
    .pill-success { background: #14532d; color: #86efac; }
    .pill-partial { background: #713f12; color: #fde047; }
    .pill-failed { background: #7f1d1d; color: #fca5a5; }
    .pill-running { background: #1e3a8a; color: #93c5fd; }
    .pill-created { background: #1f2937; color: #9ca3af; }
    .section-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.35rem;
        font-weight: 600;
    }
    .header-bar {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        flex-wrap: wrap;
    }
    .header-bar h1 {
        margin: 0;
        font-size: 1.45rem;
        font-weight: 650;
        color: #f3f4f6;
        letter-spacing: -0.03em;
    }
    .header-meta {
        color: #6b7280;
        font-size: 0.85rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    .event-line {
        font-size: 0.75rem;
        color: #9ca3af;
        padding: 0.15rem 0;
        border-bottom: 1px solid #1a1f28;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_services():
    if "services" not in st.session_state:
        default_root = Path(st.session_state.get("workspace_root") or Path.cwd()).expanduser().resolve()
        session_svc = SessionService()
        perm_svc = PermissionService()
        event_svc = EventService()
        provider_reg = ProviderRegistry()
        tool_reg = ToolRegistry()
        workspace = WorkspaceService(default_root)

        skill_svc = None
        try:
            skills_root = Path(__file__).resolve().parent / "skills"
            skill_svc = SkillService(skills_root)
            skill_svc.load_all()
        except Exception as e:
            st.session_state.skills_load_error = str(e)

        try:
            ctx_svc = ContextService(skill_service=skill_svc, project_root=default_root)
        except TypeError:
            ctx_svc = ContextService()
            if skill_svc is not None and hasattr(ctx_svc, "set_skill_service"):
                ctx_svc.set_skill_service(skill_svc)
            if hasattr(ctx_svc, "set_project_root"):
                ctx_svc.set_project_root(default_root)

        tool_reg.register(ReadTool(default_root, workspace=workspace))
        tool_reg.register(WriteTool(default_root, workspace=workspace))
        tool_reg.register(EditTool(default_root, workspace=workspace))
        try:
            tool_reg.register(ProjectSearchTool(default_root))
        except Exception:
            pass
        try:
            tool_reg.register(BashTool(default_root))
        except Exception:
            pass

        def _gh_token():
            return st.session_state.get("credentials", {}).get("github")

        tool_reg.register(GitHubTool(get_token=_gh_token))
        tool_reg.register(WebSearchTool())
        tool_reg.register(WebFetchTool())

        # PinchTab + AgentReach — fail soft so app never crashes on missing optional tools
        try:
            from src.tools.pinchtab_tool import PinchTabTool

            def _pt_url():
                return st.session_state.get("credentials", {}).get("pinchtab_url") or "http://127.0.0.1:9867"

            def _pt_token():
                return st.session_state.get("credentials", {}).get("pinchtab_token")

            tool_reg.register(PinchTabTool(get_base_url=_pt_url, get_token=_pt_token))
        except Exception as e:
            st.session_state["pinchtab_load_error"] = str(e)[:200]

        try:
            from src.tools.agent_reach_tool import AgentReachTool

            tool_reg.register(AgentReachTool())
        except Exception as e:
            st.session_state["agent_reach_load_error"] = str(e)[:200]

        source = Path(__file__).resolve().parent / "knowledge" / "source_headings.md"
        if source.exists():
            ctx_svc.load_source(source)
        knowledge_dir = Path(__file__).resolve().parent / "knowledge" / "claude_code"
        if knowledge_dir.exists() and hasattr(ctx_svc, "load_knowledge_dir"):
            n = ctx_svc.load_knowledge_dir(knowledge_dir)
            st.session_state.knowledge_chunks = n

        def get_cred(ref):
            if not ref:
                return None
            return st.session_state.get("credentials", {}).get(ref)

        try:
            runtime = AgentRuntime(
                session_svc,
                perm_svc,
                event_svc,
                ctx_svc,
                provider_reg,
                tool_reg,
                get_credential=get_cred,
                skill_service=skill_svc,
            )
        except TypeError:
            runtime = AgentRuntime(
                session_svc,
                perm_svc,
                event_svc,
                ctx_svc,
                provider_reg,
                tool_reg,
                get_credential=get_cred,
            )

        st.session_state.services = {
            "session": session_svc,
            "permission": perm_svc,
            "event": event_svc,
            "context": ctx_svc,
            "skills": skill_svc,
            "runtime": runtime,
            "providers": provider_reg,
            "tools": tool_reg,
            "workspace": workspace,
        }
        st.session_state.credentials = st.session_state.get("credentials", {})
        st.session_state.messages = st.session_state.get("messages", [])
        st.session_state.active_session_id = st.session_state.get("active_session_id")
        st.session_state.fetched_models = st.session_state.get("fetched_models", {})
        st.session_state.model_fetch_error = st.session_state.get("model_fetch_error", "")
        st.session_state.workspace_root = str(default_root)
    return st.session_state.services


def ensure_session(services, provider: str, model: str, base_url: str | None, permission_mode: str, run_mode: str = "agent"):
    root = st.session_state.get("workspace_root") or str(Path.cwd())
    if st.session_state.active_session_id:
        session = services["session"].get(st.session_state.active_session_id)
        if session:
            if hasattr(services["session"], "set_project_root"):
                services["session"].set_project_root(session.session_id, root)
            else:
                session.project_root = root
            return session
    config = ProviderConfig(
        provider=provider,
        model=model,
        base_url=base_url or None,
        credential_ref=provider,
    )
    session = services["session"].create(
        provider_config=config,
        permission_mode=PermissionMode(permission_mode),
        project_root=root,
        mode=run_mode if run_mode in ("agent", "plan") else "agent",
    )
    st.session_state.active_session_id = session.session_id
    return session


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.ensure_future(coro)
    except RuntimeError:
        pass
    return asyncio.run(coro)


async def fetch_models(services, provider: str, base_url: str, api_key: str | None) -> list[str]:
    config = ProviderConfig(
        provider=provider,
        model="probe",
        base_url=base_url or None,
        credential_ref=provider,
    )
    client = services["providers"].create(config, api_key)
    models = await client.list_models()
    return models


def _status_pill(status: str) -> str:
    s = (status or "").lower()
    cls = "pill-created"
    if s in ("succeeded", "success"):
        cls = "pill-success"
    elif s in ("partial",):
        cls = "pill-partial"
    elif s in ("failed", "cancelled"):
        cls = "pill-failed"
    elif s in ("running", "waiting_children", "waiting_permission"):
        cls = "pill-running"
    return f'<span class="status-pill {cls}">{status}</span>'


def main():
    services = get_services()
    provider_ids = [p for p in services["providers"].list_providers() if p in PROVIDER_PRESETS]
    labels = {pid: get_preset(pid).get("label", pid) for pid in provider_ids}

    with st.sidebar:
        st.markdown("### Settings")

        st.markdown('<div class="section-label">Workspace</div>', unsafe_allow_html=True)
        ws_default = st.session_state.get("workspace_root") or str(Path.cwd())
        ws_input = st.text_input(
            "Project directory",
            value=ws_default,
            help="Local absolute path agents read/write in. On Streamlit Cloud this is the repo mount; locally set your project folder.",
            key="workspace_path_input",
        )
        if st.button("Apply workspace", use_container_width=True):
            ok, msg = apply_workspace_root(services, ws_input)
            if ok:
                st.session_state.workspace_root = msg
                if st.session_state.active_session_id:
                    services["session"].set_project_root(st.session_state.active_session_id, msg)
                st.success(f"Workspace: {msg}")
            else:
                st.error(msg)
        st.caption(f"Active: `{st.session_state.get('workspace_root', ws_default)}`")

        st.divider()
        provider = st.selectbox(
            "Provider",
            provider_ids,
            format_func=lambda p: labels.get(p, p),
            index=provider_ids.index("opencode") if "opencode" in provider_ids else 0,
            key="provider_select",
        )
        preset = get_preset(provider)

        default_url = preset.get("base_url") or ""
        if "base_url_by_provider" not in st.session_state:
            st.session_state.base_url_by_provider = {}
        if provider not in st.session_state.base_url_by_provider:
            st.session_state.base_url_by_provider[provider] = default_url

        base_url = st.text_input(
            "Base URL",
            value=st.session_state.base_url_by_provider.get(provider, default_url),
            help="Must end with /v1 for OpenAI-compatible providers.",
            key=f"base_url_{provider}",
        )
        st.session_state.base_url_by_provider[provider] = base_url

        api_key = st.text_input(
            "API key / token",
            type="password",
            value=st.session_state.credentials.get(provider, ""),
            key=f"api_key_{provider}",
            disabled=(provider == "ollama"),
        )
        if api_key:
            st.session_state.credentials[provider] = api_key
        if provider == "ollama":
            st.session_state.credentials["ollama"] = st.session_state.credentials.get("ollama") or "ollama"

        fallback = services["providers"].fallback_models(provider)
        fetched = st.session_state.fetched_models.get(provider) or []
        model_options = fetched if fetched else fallback

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Fetch models", use_container_width=True):
                try:
                    models = run_async(
                        fetch_models(
                            services,
                            provider,
                            base_url.strip(),
                            st.session_state.credentials.get(provider),
                        )
                    )
                    if models and not asyncio.isfuture(models):
                        st.session_state.fetched_models[provider] = models
                        st.session_state.model_fetch_error = ""
                except Exception as e:
                    st.session_state.model_fetch_error = str(e)[:300]
        with col_b:
            if st.button("Use presets", use_container_width=True):
                st.session_state.fetched_models[provider] = []
                st.rerun()

        if st.session_state.model_fetch_error:
            st.warning(st.session_state.model_fetch_error)

        if model_options:
            default_model = preset.get("default_model") or model_options[0]
            idx = model_options.index(default_model) if default_model in model_options else 0
            model = st.selectbox("Model", model_options, index=idx, key=f"model_select_{provider}")
        else:
            model = st.text_input("Model", value=preset.get("default_model") or "", key=f"model_text_{provider}")

        perm_mode = st.selectbox("Permission mode", ["ask", "session_allow", "deny"], index=1)
        run_mode = st.selectbox(
            "Mode",
            ["agent", "plan"],
            index=0,
            key="run_mode_select",
            help="plan = specs under .agentforge/specs; limited writes. agent = full execution.",
        )

        if st.button("New session", use_container_width=True):
            st.session_state.active_session_id = None
            st.session_state.messages = []
            if services.get("workspace"):
                services["workspace"].clear_artifacts()
            st.rerun()

        st.divider()
        st.markdown('<div class="section-label">Connectors</div>', unsafe_allow_html=True)
        gh = st.text_input(
            "GitHub token",
            type="password",
            value=st.session_state.credentials.get("github", ""),
            key="gh_token_input",
        )
        if gh:
            st.session_state.credentials["github"] = gh

        st.caption("Browser (PinchTab) — only if local server is running")
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

        if services.get("skills"):
            skill_count = len(getattr(services["skills"], "_skills", {}) or {})
            st.caption(f"Skills loaded · {skill_count}")

        st.divider()
        pending = services["permission"].get_pending(st.session_state.active_session_id or "")
        if pending:
            st.markdown('<div class="section-label">Permission requests</div>', unsafe_allow_html=True)
            for req in pending:
                with st.expander(f"{req.tool_name} · {req.risk}", expanded=True):
                    st.code(str(req.tool_input)[:500])
                    c1, c2 = st.columns(2)
                    if c1.button("Approve", key=f"ok_{req.request_id}", use_container_width=True):
                        services["permission"].decide(req.request_id, PermissionDecision.APPROVED)
                        st.rerun()
                    if c2.button("Deny", key=f"no_{req.request_id}", use_container_width=True):
                        services["permission"].decide(req.request_id, PermissionDecision.DENIED)
                        st.rerun()

    if not model:
        st.error("Select or type a model name before running tasks.")
        return

    session = ensure_session(services, provider, model, base_url.strip() or None, perm_mode, run_mode=run_mode)
    services["permission"].set_mode(PermissionMode(perm_mode))
    if hasattr(services["session"], "set_mode"):
        services["session"].set_mode(session.session_id, run_mode)
    if session.provider_config:
        session.provider_config.provider = provider
        session.provider_config.model = model
        session.provider_config.base_url = base_url.strip() or None
        session.provider_config.credential_ref = provider

    mode_label = "PLAN" if getattr(session, "mode", "agent") == "plan" else "AGENT"
    st.markdown(
        f"""
        <div class="header-bar">
            <h1>Claude Code Replica</h1>
            <span class="header-meta">session {session.session_id[:8]} · {provider}/{model} · {mode_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"Workspace · `{st.session_state.get('workspace_root', '')}`")

    col_chat, col_side = st.columns([2.0, 1.15])

    with col_chat:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Describe the task...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Running agents..."):
                    try:
                        result = run_async(
                            services["runtime"].run_task(
                                session.session_id,
                                prompt,
                                project_context=f"Workspace root: {st.session_state.get('workspace_root', '')}",
                            )
                        )
                        if asyncio.isfuture(result) or hasattr(result, "__await__"):
                            result = {"status": "running", "summary": "task submitted"}
                        summary = result.get("summary") or str(result)
                        status = result.get("status", "unknown")
                        arts = []
                        if services.get("workspace"):
                            arts = [a["path"] for a in services["workspace"].list_artifacts(limit=12)]
                        reply = f"**{status}**\n\n{summary}"
                        if arts:
                            reply += "\n\n**Files touched**\n" + "\n".join(f"- `{p}`" for p in arts)
                    except Exception as e:
                        reply = f"Error: {e}"
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

    with col_side:
        render_artifacts_panel(st, services)

        st.markdown('<div class="section-label" style="margin-top:1rem">Multi-agent</div>', unsafe_allow_html=True)
        tree = services["runtime"].get_agent_tree(session.session_id)
        if tree:
            for node in tree:
                indent = "&nbsp;" * (node["depth"] * 4)
                status = node["status"]
                st.markdown(
                    f"""
                    <div class="agent-node {status}">
                        {indent}<strong>{node['domain']}</strong> {_status_pill(status)}<br/>
                        {indent}<span style="opacity:0.75">{node['objective']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No agents yet")

        st.markdown('<div class="section-label" style="margin-top:1rem">Events</div>', unsafe_allow_html=True)
        events = services["event"].list_events(session.session_id, limit=30)
        for ev in reversed(events[-8:]):
            st.markdown(
                f'<div class="event-line">{ev.event_type.value}: {ev.message[:90]}</div>',
                unsafe_allow_html=True,
            )

        if st.button("Cancel session", use_container_width=True):
            services["runtime"].cancel(session.session_id)
            st.warning("Cancellation requested")


if __name__ == "__main__":
    main()
