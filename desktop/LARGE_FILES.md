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

Slices are 8 KB each (45 parts: launch_engine 25 + pack_portable 20) so the GitHub connector can accept them in small batches. Checksums live in `desktop/parts/PARTS_SHA256.txt`. After join, compare those hashes before copying the rebuilt files to `desktop/`.

Remote as of 2026-09-14 20:31 PKT: GitHub `app.py` SHA 57e524ef (full 655 lines / 26092 bytes, no PLACEHOLDER). pack_portable.py.part02 on main is still truncated (~1910 bytes vs local 8000). Join tests 3 passed locally. Next run: restore pack parts 02–19 at 8000 bytes each, then full `pack_portable.py` / `launch_engine.py`.

5. Open `/ui/`
6. Use `desktop/windows/Start-AgentForge.bat` only after full `launch_engine.py` is present
