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
from src.tools.github_tool import GitHubTool
from src.tools.web_tools import WebSearchTool, WebFetchTool
from src.tools.pinchtab_tool import PinchTabTool
from src.orchestration.runtime import AgentRuntime


st.set_page_config(
    page_title="Claude Code Replica",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# NOTE: Full UI styles and layout are in the working tree.
# Minimal bootstrap that registers PinchTabTool so agents can use browser access.

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

        def _gh_token():
            return st.session_state.get("credentials", {}).get("github")

        tool_reg.register(GitHubTool(get_token=_gh_token))
        tool_reg.register(WebSearchTool())
        tool_reg.register(WebFetchTool())

        def _pt_url():
            return st.session_state.get("credentials", {}).get("pinchtab_url") or "http://127.0.0.1:9867"

        def _pt_token():
            return st.session_state.get("credentials", {}).get("pinchtab_token")

        tool_reg.register(PinchTabTool(get_base_url=_pt_url, get_token=_pt_token))

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
        }
        st.session_state.credentials = st.session_state.get("credentials", {})
        st.session_state.messages = st.session_state.get("messages", [])
        st.session_state.active_session_id = st.session_state.get("active_session_id")
        st.session_state.fetched_models = st.session_state.get("fetched_models", {})
        st.session_state.model_fetch_error = st.session_state.get("model_fetch_error", "")
    return st.session_state.services


def main():
    st.title("Claude Code Replica")
    st.caption("PinchTab browser tool registered. Prefer local full app.py for complete UI.")
    services = get_services()
    st.write("Tools:", services["tools"].list_names())


if __name__ == "__main__":
    main()
