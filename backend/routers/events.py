from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.engine import get_engine

router = APIRouter()


@router.get("/{session_id}")
async def stream_events(session_id: str, after: int = 0):
    engine = get_engine()
    if engine.get_session(session_id) is None:
        raise HTTPException(404, "session not found")

    async def gen():
        cursor = after
        idle = 0
        while idle < 300:
            batch = engine.session_events(session_id, after=cursor)
            if batch:
                idle = 0
                for ev in batch:
                    cursor = ev["index"] + 1
                    yield f"data: {json.dumps(ev)}\n\n"
            else:
                idle += 1
                yield ": keepalive\n\n"
                await asyncio.sleep(0.4)
        yield f"data: {json.dumps({'type': 'stream_end', 'index': cursor})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
