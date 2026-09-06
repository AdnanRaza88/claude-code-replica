# AgentForge (AI Engineer OS) — Standing Automation Instructions

**Read this file first on every run.** Then read `automation/state.json` and `docs/DESKTOP_BUILD_PHASES.md` and `STRUCTURE.md`.

Product name: **AgentForge (AI Engineer OS)** (not Claude Code Replica).

---

## 1. Tech stack (do not drift)

| Layer | Use | Do not |
|-------|-----|--------|
| Language | Python 3.11+, vanilla-first | Heavy frameworks without need |
| API | FastAPI + Uvicorn | Put business logic only in routers |
| Models | Pydantic v2 | Untyped dicts for domain |
| Orchestration | Existing TaskGraph + AgentRuntime + harness | Rewrite core runtime from scratch |
| LLM providers | OpenCode Zen/Inference + Gemini (+ Ollama/Groq adapters) | Hardcode broken model IDs |
| UI | `frontend/` liquid-glass light → talks only to FastAPI | New logic in Streamlit `app.py` |
| Desktop | Tauri 2 wrapping `/ui` + local FastAPI | Electron unless Tauri blocked |
| Optional | LangChain/LangGraph only if a graph clearly helps | Force LangGraph for simple flows |
| Data | `.agentforge/` sessions + memory | Secrets in git |

**Rule:** Logic in `src/`. HTTP in `backend/`. Look in `frontend/`. Map in `STRUCTURE.md`.

---

## 2. What to integrate (open source)

Integrate only what maps to tools, skills, agents, or MCPs. Prefer MIT/Apache.

**Already in path (keep working):** Superpowers patterns, ECC-style specialists, humanizer, defuddle, Agent-Reach, local code_graph, security harness.

**Next when phase allows:**
- Graphify / codebase-memory-mcp (full MCP or deeper graph)
- Caveman-style token efficiency if cost bites
- Selective Composio for external apps
- Never dump unrelated marketing/video packs into core coding path

Catalog: `artifacts/resources/OPEN_SOURCE_RESOURCES_CATALOG.md` and `STRUCTURE.md` section 11.

---

## 3. How each run must work

1. Read this file + `state.json` + current phase in `DESKTOP_BUILD_PHASES.md`.
2. Do **1–3 concrete shippable tasks** only for the current phase.
3. Do not skip phases. Do not big-bang rewrite.
4. After work: update `state.json` (`completed_steps`, `pending_steps`, `last_run_at` ISO).
5. Write a short log under `automation/runs/YYYYMMDD-HHMM.md`.
6. If exit criteria met → advance `current_phase` and set next `pending_steps` from phases doc.
7. Keep engine UI-free. Touch `STRUCTURE.md` when adding a service or tool.

---

## 4. MCP servers and tools — mandatory testing

Any **MCP** we add or expose (Graphify, codebase-memory, future memory/filesystem/github MCPs, or our own MCP wrappers) must ship with tests.

### 4.1 CRUD coverage (required)

For every MCP tool surface that mutates or reads resources, tests must cover:

| Op | Meaning | Example |
|----|---------|---------|
| **C** Create | Create resource / index / node / session artifact | create index, create note, add graph node |
| **R** Read | Fetch / query / list / get by id | query_graph, get_node, list tools |
| **U** Update | Patch / reindex / update fields | update node, reindex file, rename |
| **D** Delete | Remove / clear / drop | delete node, clear index, drop session artifact |

If a tool is **read-only** by design (e.g. pure search), document that and still test **R** thoroughly (empty, hit, miss, bad input). Do not invent fake write tools.

### 4.2 Where tests live

- `tests/test_mcp_*.py` or `tests/mcp/` per server
- Or tool-level: `tests/test_tools_code_graph.py` style for local graph
- Use pytest; async if the tool is async
- Prefer temp dirs / temp workspaces; never delete user project data

### 4.3 Minimum test matrix per MCP or tool pack

1. Happy path Create → Read back → Update → Read → Delete → Read miss  
2. Invalid input / missing id returns clear error (no crash)  
3. Permission / sandbox: cannot escape workspace root  
4. Idempotent where claimed (e.g. reindex no-op)  
5. Smoke: tool appears in registry / `/tools` list if exposed via API  

### 4.4 When you add an MCP in a run

- Implement or wire the MCP/tool  
- Add CRUD (or R-only) tests in the same run or the immediately next run  
- Mark in `state.json` completed_steps: `"MCP <name>: CRUD tests added"`  
- Do not mark phase complete if MCP was added without tests  

### 4.5 Local stand-ins

`code_graph_tool` is our local graph stand-in. Treat it like an MCP resource API: index (C/U), query/symbol/outline (R), clear/reindex policies (U/D as applicable) must stay tested under `tests/`.

---

## 5. Quality gates every few runs

- `pytest` on touched modules (at least new tests)  
- FastAPI `/health` still OK  
- No secrets committed  
- `STRUCTURE.md` updated if new service/tool attachment  

---

## 6. Phase pointer

Current phase is only in `automation/state.json`.  
Desktop (Tauri) = Phase 4. Do not jump to polish features that skip desktop exit criteria unless state says otherwise.

---

## 7. One-line mission

Advance AgentForge toward a reliable Windows desktop AI Engineer OS: thin FastAPI, rich `src/`, liquid-glass UI, tested tools/MCPs (CRUD), open-source only where it strengthens the engine.

---

## 8. GitHub commit + push (mandatory every run that changes code)

**Repo:** `AdnanRaza88/claude-code-replica` (branch `main`)  
**Product on GitHub may still show old name; code identity is AgentForge.**

### Every code-changing run must:

1. Local: `git add` changed paths (never `.agentforge/sessions`, secrets, `target/`, `__pycache__`).
2. Local: `git commit -m "AgentForge: <short what changed>"` if there is anything staged.
3. Remote: push changed files to GitHub using the **GitHub connected tool** `github___push_files` (owner `AdnanRaza88`, repo `claude-code-replica`, branch `main`).
   - Prefer **batches of 5–15 files** per commit (API-friendly).
   - Commit message prefix: `AgentForge:`.
   - Do not skip push because "too many files" — push the **new/changed** set this run; continue backlog next run.
4. Track backlog in `automation/state.json` under key `github_push_backlog` (list of relative paths not yet on remote).
5. After push, remove pushed paths from backlog; add note to `automation/runs/`.

### First full sync backlog (if still open)

Priority order to clear onto GitHub:
1. `backend/` (all)
2. `frontend/`
3. `automation/`
4. `desktop/` (scripts + VERSION + launch/pack, then src-tauri)
5. `src/` (tools, services, orchestration, harness, adapters)
6. `skills/`
7. `tests/`, `docs/`, `.github/workflows/`

### Do not

- Force-push or rewrite published history without user ask
- Commit API keys or `.env`
- Assume `git push` HTTPS works without credentials — use GitHub connector `push_files`
