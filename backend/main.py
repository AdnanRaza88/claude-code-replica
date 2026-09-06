"""
FastAPI headless engine.
Streamlit / future web UI / Tauri desktop all talk to this process.
Business logic stays in src/; this package only exposes HTTP.
"""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

# Allow importing project src when running from backend/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.routers import events, health, providers, run, sessions, settings, skills, tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure workspace paths exist, load skills registry if needed
    yield
    # Shutdown hooks if any


app = FastAPI(
    title="AgentForge Engine",
    description="Headless multi-agent coding engine. Desktop and web UI are thin clients.",
    version="0.4.19",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production desktop
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(sessions.router, prefix="/session", tags=["session"])
app.include_router(run.router, prefix="/run", tags=["run"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(providers.router, prefix="/providers", tags=["providers"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])
app.include_router(skills.router, prefix="/skills", tags=["skills"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])

FRONTEND = ROOT / "frontend"
if FRONTEND.is_dir():
    app.mount("/ui", StaticFiles(directory=str(FRONTEND), html=True), name="ui")


@app.get("/")
async def root():
    index = FRONTEND / "index.html"
    if index.is_file():
        return RedirectResponse(url="/ui/")
    return {
        "service": "agentforge-engine",
        "version": "0.4.38",
        "docs": "/docs",
        "health": "/health",
        "desktop": "/desktop/status",
        "onboard": "/desktop/onboard",
        "windows_path": "/desktop/windows-path",
        "ci_trigger": "/desktop/ci-trigger",
        "ci_watch": "/desktop/ci-watch",
        "ci_pull": "/desktop/ci-pull",
        "ci_install": "/desktop/ci-install",
        "ci_verify": "/desktop/ci-verify",
        "ci_go": "/desktop/ci-go",
        "windows_host": "/desktop/windows-host",
        "ci_drop": "/desktop/ci-drop",
        "ci_apply": "/desktop/ci-apply",
        "ci_finish": "/desktop/ci-finish",
        "ci_live": "/desktop/ci-live",
        "ci_boot": "/desktop/ci-boot",
        "ci_seal": "/desktop/ci-seal",
        "ci_exit": "/desktop/ci-exit",
        "remain": "/desktop/remain",
        "host_block": "/desktop/host-block",
        "ui": "/ui/",
    }


@app.get("/app")
async def app_alias():
    return FileResponse(FRONTEND / "index.html")
