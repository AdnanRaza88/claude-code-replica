from __future__ import annotations

import asyncio
import os
from pathlib import Path

import streamlit as st

from src.models.provider import ProviderConfig
from src.models.permission import PermissionMode, PermissionDecision
from src.services.session_service import SessionService
from src.services.permission_service import PermissionService
from src.services.event_service import EventService
from src.services.context_service import ContextService
from src.adapters.providers.registry import ProviderRegistry
from src.tools.base import ToolRegistry
from src.tools.file_tools import ReadTool, WriteTool, EditTool
from src.tools.search_tools import ProjectSearchTool
from src.tools.bash_tool import BashTool
from src.orchestration.runtime import AgentRuntime


st.set_page_config(page_title="Claude Code Replica", layout="wide", initial_sidebar_state="expanded")


def get_services():
    if "services" not in st.session_state:
        session_svc = SessionService()
        perm_svc = PermissionService()
        event_svc = EventService()
        ctx_svc = ContextService()
        provider_reg = ProviderRegistry()
        tool_reg = ToolRegistry()

        root = Path.cwd()
        tool_reg.register(ReadTool(root))
        tool_reg.register(WriteTool(root))
        tool_reg.register(EditTool(root))
        tool_reg.register(ProjectSearchTool(root))
        tool_reg.register(BashTool(root))

        source = Path(__file__).parent / "knowledge" / "source_headings.md"
        if source.exists():
            ctx_svc.load_source(source)

        def get_cred(ref: str | None) -> str | None:
            if not ref:
                return None
            return st.session_state.get("credentials", {}).get(ref)

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
            "runtime": runtime,
            "providers": provider_reg,
        }
        st.session_state.credentials = st.session_state.get("credentials", {})
        st.session_state.messages = st.session_state.get("messages", [])
        st.session_state.active_session_id = st.session_state.get("active_session_id")
    return st.session_state.services


def ensure_session(services, provider: str, model: str, base_url: str | None, mode: str):
    if st.session_state.active_session_id:
        session = services["session"].get(st.session_state.active_session_id)
        if session:
            return session
    config = ProviderConfig(
        provider=provider,
        model=model,
        base_url=base_url or None,
        credential_ref=provider,
    )
    session = services["session"].create(
        provider_config=config,
        permission_mode=PermissionMode(mode),
        project_root=str(Path.cwd()),
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


def main():
    services = get_services()
    providers = services["providers"].list_providers()

    with st.sidebar:
        st.title("Settings")
        provider = st.selectbox("Provider", providers, index=providers.index("ollama") if "ollama" in providers else 0)
        model = st.text_input("Model", value="llama3.2")
        base_url = st.text_input("Base URL (optional)", value="")
        api_key = st.text_input("API key / token", type="password", value="")
        if api_key:
            st.session_state.credentials[provider] = api_key

        perm_mode = st.selectbox("Permission mode", ["ask", "session_allow", "deny"], index=0)
        app_mode = st.selectbox("Mode", ["agent", "plan"], index=0)

        if st.button("New session"):
            st.session_state.active_session_id = None
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.caption("Connectors")
        st.text_input("GitHub token", type="password", key="gh_token")
        if st.session_state.get("gh_token"):
            st.session_state.credentials["github"] = st.session_state.gh_token

        st.divider()
        pending = services["permission"].get_pending(st.session_state.active_session_id or "")
        if pending:
            st.subheader("Permission requests")
            for req in pending:
                with st.expander(f"{req.tool_name} ({req.risk})"):
                    st.code(str(req.tool_input)[:500])
                    c1, c2 = st.columns(2)
                    if c1.button("Approve", key=f"ok_{req.request_id}"):
                        services["permission"].decide(req.request_id, PermissionDecision.APPROVED)
                        st.rerun()
                    if c2.button("Deny", key=f"no_{req.request_id}"):
                        services["permission"].decide(req.request_id, PermissionDecision.DENIED)
                        st.rerun()

    session = ensure_session(services, provider, model, base_url or None, perm_mode)
    services["permission"].set_mode(PermissionMode(perm_mode))
    if session.provider_config:
        session.provider_config.provider = provider
        session.provider_config.model = model
        session.provider_config.base_url = base_url or None
        session.provider_config.credential_ref = provider

    st.title("Claude Code Replica")
    st.caption(f"Session {session.session_id[:8]} · {provider}/{model}")

    col_chat, col_side = st.columns([2, 1])

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
                            services["runtime"].run_task(session.session_id, prompt)
                        )
                        if asyncio.isfuture(result) or hasattr(result, "__await__"):
                            result = {"status": "running", "summary": "task submitted"}
                        summary = result.get("summary") or str(result)
                        status = result.get("status", "unknown")
                        reply = f"**{status}**\n\n{summary}"
                    except Exception as e:
                        reply = f"Error: {e}"
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

    with col_side:
        st.subheader("Agent tree")
        tree = services["runtime"].get_agent_tree(session.session_id)
        if tree:
            for node in tree:
                indent = " " * node["depth"]
                st.text(f"{indent}{node['domain']} [{node['status']}]")
                st.caption(f"{indent}{node['objective']}")
        else:
            st.caption("No agents yet")

        st.subheader("Events")
        events = services["event"].list_events(session.session_id, limit=30)
        for ev in reversed(events[-15:]):
            st.caption(f"{ev.event_type.value}: {ev.message[:80]}")

        if st.button("Cancel session"):
            services["runtime"].cancel(session.session_id)
            st.warning("Cancellation requested")


if __name__ == "__main__":
    main()
