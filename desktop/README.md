# AgentForge desktop shell (Tauri 2)

Wraps the liquid-glass UI at `/ui/` and a local FastAPI process.

## Dev (no installer)

From the repo root:

```
python desktop/launch_engine.py
```

Then open `http://127.0.0.1:8787/ui/`.

Windows checkout (no Tauri build):

```
desktop\windows\Start-AgentForge.bat
```

Portable folder:

```
python desktop/pack_portable.py
```

Windows installer script (needs NSIS on the build PC):

```
powershell -ExecutionPolicy Bypass -File desktop\windows\build_installer.ps1
```

Or with Tauri (requires Rust + WebView2 on Windows):

```
cd desktop/src-tauri
cargo tauri dev
```

The Rust shell starts `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787` from the project root and loads the UI. Override interpreter with `AGENTFORGE_PYTHON`.

## Settings

Keys and connector URLs live in `.agentforge/settings.json` (mode 600 when the OS allows). HTTP:

- `GET /settings` masked
- `GET /settings?reveal=true` full local values
- `PUT /settings` patch
- `DELETE /settings` clear file

Fields: Gemini / OpenCode / OpenAI / Groq keys, Ollama base URL, GitHub token, PinchTab URL/token, Agent-Reach base/token, engine host/port, workspace.
