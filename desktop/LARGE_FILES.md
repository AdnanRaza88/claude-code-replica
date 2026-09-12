# Large desktop scripts not yet on GitHub

These two files exist locally and are required for a full Windows pack. The GitHub connector payload limit blocks a single-commit push of their full text.

| Path | Local size | Role |
|------|------------|------|
| `desktop/launch_engine.py` | ~198 KB / 4241 lines | Engine start/stop/doctor + Phase-4 host packets |
| `desktop/pack_portable.py` | ~152 KB / 3492 lines | Builds the portable zip layout |

Until they land on `main`, a clone can still:

1. Start the FastAPI engine: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787`
2. Open `/ui/`
3. Use `desktop/windows/Start-AgentForge.bat` only after `launch_engine.py` is present

Next automation runs should keep trying `github___push_files` for these two paths alone.
