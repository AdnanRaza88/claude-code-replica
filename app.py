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
from src.adapters.providers.registry import ProviderRegistry
from src.adapters.providers.presets import get_preset, PROVIDER_PRESETS
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
        provider_reg = ProviderRegistry()
        tool_reg = ToolRegistry()

        skill_svc = None
        try:
            skills_root = Path(__file__).resolve().parent / "skills"
            skill_svc = SkillService(skills_root)
            skill_svc.load_all()
        except Exception as e:
            st.session_state.skills_load_error = str(e)

        try:
            ctx_svc = ContextService(skill_service=skill_svc)
        except TypeError:
            ctx_svc = ContextService()
            if skill_svc is not None and hasattr(ctx_svc, "set_skill_service"):
                ctx_svc.set_skill_service(skill_svc)

        root = Path.cwd()
        tool_reg.register(ReadTool(root))
        tool_reg.register(WriteTool(root))
        tool_reg.register(EditTool(root))
        tool_reg.register(ProjectSearchTool(root))
        tool_reg.register(BashTool(root))

        source = Path(__file__).resolve().parent / "knowledge" / "source_headings.md"
        if source.exists():
            ctx_svc.load_source(source)

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
        }
        st.session_state.credentials = st.session_state.get("credentials", {})
        st.session_state.messages = st.session_state.get("messages", [])
        st.session_state.active_session_id = st.session_state.get("active_session_id")
        st.session_state.fetched_models = st.session_state.get("fetched_models", {})
        st.session_state.model_fetch_error = st.session_state.get("model_fetch_error", "")
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


def main():
    services = get_services()
    provider_ids = [p for p in services["providers"].list_providers() if p in PROVIDER_PRESETS]
    labels = {pid: get_preset(pid).get("label", pid) for pid in provider_ids}

    with st.sidebar:
        st.title("Settings")

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
            help="Must end with /v1 for OpenAI-compatible providers",
            key=f"base_url_{provider}",
        )
        st.session_state.base_url_by_provider[provider] = base_url

        api_key = st.text_input(
            "API key / token",
            type="password",
            value=st.session_state.credentials.get(provider, ""),
            help="Required for OpenCode, Zen, Groq, OpenAI, Gemini",
            key=f"api_key_{provider}",
        )
        if api_key:
            st.session_state.credentials[provider] = api_key

        fallback = services["providers"].fallback_models(provider)
        fetched = st.session_state.fetched_models.get(provider) or []
        model_options = fetched if fetched else fallback

        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Fetch models", use_container_width=True):
                if not base_url.strip():
                    st.session_state.model_fetch_error = "Base URL required"
                else:
                    try:
                        models = run_async(
                            fetch_models(
                                services,
                                provider,
                                base_url.strip(),
                                st.session_state.credentials.get(provider),
                            )
                        )
                        if asyncio.isfuture(models):
                            st.session_state.model_fetch_error = "Could not run model fetch in this context"
                        elif models:
                            st.session_state.fetched_models[provider] = models
                            st.session_state.model_fetch_error = ""
                            st.success(f"{len(models)} models loaded")
                        else:
                            st.session_state.model_fetch_error = (
                                "No models returned. Check base URL and API key. "
                                "Preset list will be used."
                            )
                    except Exception as e:
                        st.session_state.model_fetch_error = str(e)[:300]
        with col_b:
            if st.button("Use presets", use_container_width=True):
                st.session_state.fetched_models[provider] = []
                st.session_state.model_fetch_error = ""
                st.rerun()

        if st.session_state.model_fetch_error:
            st.warning(st.session_state.model_fetch_error)

        if model_options:
            default_model = preset.get("default_model") or model_options[0]
            idx = model_options.index(default_model) if default_model in model_options else 0
            model = st.selectbox("Model", model_options, index=idx, key=f"model_select_{provider}")
        else:
            model = st.text_input(
                "Model",
                value=preset.get("default_model") or "",
                key=f"model_text_{provider}",
            )

        st.caption(f"Active: `{provider}` / `{model}`")
        if base_url:
            st.caption(f"URL: `{base_url}`")

        perm_mode = st.selectbox("Permission mode", ["ask", "session_allow", "deny"], index=0)
        st.selectbox("Mode", ["agent", "plan"], index=0)

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

    if not model:
        st.error("Select or type a model name before running tasks.")
        return

    session = ensure_session(services, provider, model, base_url.strip() or None, perm_mode)
    services["permission"].set_mode(PermissionMode(perm_mode))
    if session.provider_config:
        session.provider_config.provider = provider
        session.provider_config.model = model
        session.provider_config.base_url = base_url.strip() or None
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
                indent = "\u2003" * node["depth"]
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
