"""Smoke tests for AgentReachTool — no paid APIs, fail soft."""
from __future__ import annotations

import asyncio
import pytest

from src.tools.agent_reach_tool import AgentReachTool


@pytest.fixture
def tool():
    return AgentReachTool()


def test_name_and_risk(tool):
    assert tool.name == "agent_reach"
    assert tool.risk == "low"


@pytest.mark.asyncio
async def test_doctor(tool):
    r = await tool.execute({"action": "doctor"})
    assert r.success is True
    assert "jina_reader" in (r.output or "")
    assert "wikipedia" in (r.output or "").lower() or "wikipedia" in (r.data or {})


@pytest.mark.asyncio
async def test_unknown_action(tool):
    r = await tool.execute({"action": "not_a_real_action"})
    assert r.success is False
    assert r.error


@pytest.mark.asyncio
async def test_web_read_requires_url(tool):
    r = await tool.execute({"action": "web_read"})
    assert r.success is False


@pytest.mark.asyncio
async def test_wikipedia_requires_query(tool):
    r = await tool.execute({"action": "wikipedia"})
    assert r.success is False


@pytest.mark.asyncio
async def test_x_hint(tool):
    r = await tool.execute({"action": "x_search_hint"})
    assert r.success is True
    assert "xreach" in (r.output or "").lower() or "twitter" in (r.output or "").lower()
