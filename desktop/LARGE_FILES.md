# Large desktop scripts not yet on GitHub as single files

These two files exist locally and are required for a full Windows pack. The GitHub connector payload limit blocks a single-commit push of their full text.

| Path | Local size | Role |
|------|------------|------|
| `desktop/launch_engine.py` | ~198 KB / 4241 lines | Engine start/stop/doctor + Phase-4 host packets |
| `desktop/pack_portable.py` | ~152 KB / 3492 lines | Builds the portable zip layout |

Until the single files land on `main`, a clone can still:

1. Start the FastAPI engine: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787`
2. Or use the slim launcher on GitHub: `python desktop/launch_engine_min.py` (start / `--status` / `--stop` / `--doctor` / `--open-ui`)
3. Build a slim portable folder: `python desktop/pack_portable_min.py`
4. Rebuild the full scripts from parts:

```
python desktop/parts/join_large_files.py
```

That writes `desktop/parts/launch_engine.py` and `desktop/parts/pack_portable.py`. Copy them up one folder if you need the historical paths.

5. Open `/ui/`
6. Use `desktop/windows/Start-AgentForge.bat` only after full `launch_engine.py` is present
