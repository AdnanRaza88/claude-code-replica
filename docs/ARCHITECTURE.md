# Architecture (surfaces + engine)

## Rule

All product logic lives in a **headless engine**. UIs are adapters.

```
src/tools/           # tools (UI-free)
src/orchestration/   # planner + runtime
src/services/        # permissions, context, session, events, skills
src/harness/         # think/act loop, budgets
src/adapters/        # LLM providers, GitHub, future STT/MCP
app.py               # Streamlit adapter (temporary)
cli/                 # future terminal
web/ + src/api/      # future HTML/JS + FastAPI
desktop/             # future Tauri shell only
```

## Surfaces (order)

1. Engine library (already mostly here)  
2. Terminal CLI  
3. Web UI + Docker (replace Streamlit)  
4. Desktop shell last (Mac/Windows via Tauri preferred)

## Cross-platform

- `pathlib` only; no hardcoded `/Users/...`  
- Subprocess tools respect OS but blocklists stay generic  
- Docker is the “same everywhere” distribution path for non-dev users  

## Parallel execution

- Task graph + child agents  
- Shared bible in every pack  
- Waves + barrier integration  
- Permission + token gates before large swarms  

## Streamlit

Temporary. Do not put new business logic only in `app.py`.
