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
from src.tools.agent_reach_tool import AgentReachTool
from src.tools.memory_tool import MemoryTool
from src.tools.code_graph_tool import CodeGraphTool
from src.tools.text_tools import DefuddleTool, HumanizeTool
from src.orchestration.runtime import AgentRuntime


st.set_page_config(
    page_title="AgentForge (AI Engineer OS)",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)
