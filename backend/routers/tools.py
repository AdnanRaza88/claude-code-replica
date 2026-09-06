from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.engine import get_engine

router = APIRouter()


@router.get("")
async def list_tools():
    tools = get_engine().list_tools()
    return {"tools": tools, "count": len(tools)}


@router.get("/{name}")
async def get_tool(name: str):
    for tool in get_engine().list_tools():
        if tool["name"] == name:
            return tool
    raise HTTPException(404, "tool not found")
