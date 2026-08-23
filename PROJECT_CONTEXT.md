# Claude Code Replica — Project Context (Handoff)

Use this in a fresh chat to continue work without re-discovering the repo.

## What this is

Streamlit Cloud app: Claude Code–style coding workspace powered by a **dynamic hierarchical multi-agent runtime** (task graph, not a fixed swarm of N agents).

- **Repo:** https://github.com/AdnanRaza88/claude-code-replica  
- **Local path:** `/home/workdir/artifacts/claude-code-replica/`  
- **Entry:** `app.py` (`streamlit run app.py`)  
- **Stack:** Python, Streamlit, Pydantic, httpx, asyncio  
- **Not:** fixed 50-agent roster, LangGraph production graph, or full Claude Code clone

## Spec vs implementation

| Spec (PRD / TRD / orchestration_spec) | Current code |
|--------------------------------------|--------------|
| Unit of scale = **domain coverage**, not agent count | True in design; thin in practice |
| ~18 capability domains | Planner has **7 keyword domains** + `general` |
| Task graph + dynamic spawn | Yes — `TaskGraph` + `AgentRuntime` |
| Depth 4, max 8 children, ~32 active, spawn budget 64 | Enforced in `BudgetState` / `can_spawn` |
| Permission-gated tools | Yes — `PermissionService` + sidebar approve/deny |
| Context partitioning (heading index) | Partial — `ContextService` + `knowledge/source_headings.md` |
| LLM planner / rich decomposition | **No** — keyword + word-count heuristics |
| Verification agents / multi-lens checks | Result contract only; no real verifier loop |
| Durable LangGraph checkpoints | **No** — in-memory graph + asyncio |
| Connectors (GitHub first) | Stub `src/adapters/connectors/github.py` |

**Rule from PRD:** do not aim for “50 agents.” Aim for domain coverage + spawn-when-useful.

## Architecture (as built)

```
User prompt (Streamlit)
  → SessionService + ProviderConfig (single provider per session)
  → Planner.create_graph(objective)     # keyword domain detect
  → TaskGraph (root ± domain children)
  → AgentRuntime
       spawn AgentState per task
       if children → asyncio.gather parallel
       else leaf → provider.invoke + optional tools
  → PermissionService on every tool call
  → EventService (created/started/tool_*/completed/failed)
  → UI: chat + agent tree + events + permission panel
```

### Key modules

| Path | Role |
|------|------|
| `app.py` | Streamlit shell, credentials, model picker, chat, tree |
| `src/orchestration/planner.py` | Domain keywords, graph build |
| `src/orchestration/runtime.py` | Spawn, execute, children, tools, cancel |
| `src/models/agent.py` | `AgentState`, `BudgetState`, status enum |
| `src/models/task.py` | `Task`, `TaskGraph`, deps, ready_tasks |
| `src/models/provider.py` | Messages, ProviderConfig, ToolSpec |
| `src/services/permission_service.py` | ask / session_allow / deny |
| `src/services/context_service.py` | Context packs (domain-scoped) |
| `src/services/session_service.py` | Session + provider binding |
| `src/services/event_service.py` | Runtime events |
| `src/adapters/providers/` | Registry, presets, OpenAI-compatible, Ollama, Groq, Gemini |
| `src/adapters/providers/presets.py` | Base URLs + **live model lists** (Zen/OpenCode) |
| `src/tools/` | read, write, edit, search, bash |
| `config/defaults.yaml` | Budgets + provider defaults |
| `knowledge/source_headings.md` | Partitioned source index |

### Planner domains today

`git`, `browser`, `design`, `planning`, `memory`, `tools`, `scheduling`, fallback `general`.

Simple prompts (“Hi”) → **one** `general` agent. Multi-keyword / long objectives → root + children.

## Providers (important)

- Single provider/model per session; all agents inherit it.
- **OpenCode Zen** base: `https://opencode.ai/zen/v1`  
- **OpenCode Inference** base: `https://opencode.ai/inference/openai/v1`  
- Deprecated / broken model IDs: `glm-4.6`, old `kimi-k2` alone — use live IDs (`big-pickle`, `glm-5.2`, `kimi-k2.7-code`, free `*-free` models).
- UI: Provider select → Base URL → API key → **Fetch models** or presets → Model selectbox.
- Client: `OpenAICompatibleProvider` → `/chat/completions` + `/models`.

## Harness (what exists)

- Budgets: depth, children, tokens, wall-clock, spawn remaining  
- Permissions: no silent tool execution  
- Events: observability for tree + sidebar  
- Cancel flag propagates per session  
- Context packs: avoid dumping full source into every agent  

## What to build next (if extending multi-agent / graph / automation)

**Do**

1. Expand **domain registry** (prompts + tool allowlists + skills) toward ~18 PRD domains — still dynamic spawn, not fixed 50 processes.
2. Upgrade **Planner** to LLM-assisted decomposition (structured JSON tasks) with keyword fallback.
3. Add **verification** phase: independent checks (correctness / security / coverage) as optional child or post-step.
4. Harden **permission wait** (UI-driven resume, no fragile poll timeouts).
5. Optional **LangGraph** (or similar) only if durable checkpoints / human-in-the-loop barriers are required for production.
6. Automations: session-level scheduled/re-run tasks only if product needs them; keep inside Streamlit constraints (no long daemons on Streamlit Cloud).
7. Keep **human-written style**: simple professional code, **no comments spam, no emojis, no AI-flavored noise**.
8. Push to GitHub as you go (`AdnanRaza88/claude-code-replica`).

**Do not**

1. Hard-code 50 always-on agents or a permanent swarm.
2. Inject full `claude-code-fable` / giant source into every agent prompt.
3. Bypass permission service for tools.
4. Mix multiple LLM providers in one session (single-provider invariant).
5. Use deprecated Zen model IDs (`glm-4.6`, etc.).
6. Add heavy infra (Redis, workers, always-on processes) unless leaving Streamlit Cloud constraints on purpose.
7. Replace the whole runtime casually without keeping Task / AgentState / result contract shapes stable.

## Result contract (keep stable)

Child/parent results should stay:

```json
{
  "status": "success|partial|failed",
  "summary": "...",
  "artifacts": [],
  "findings": [],
  "open_questions": [],
  "verification": {}
}
```

## Run / test locally

```bash
cd /home/workdir/artifacts/claude-code-replica
pip install -r requirements.txt
streamlit run app.py
```

Sidebar: pick **OpenCode Zen**, URL `https://opencode.ai/zen/v1`, API key, model `big-pickle` or `glm-5.2` (not `glm-4.6`).

## Spec sources (attachments / knowledge)

Original intent lives in uploaded specs (PRD, TRD, orchestration_spec, context_partitioning, provider_connector_spec, implementation_plan). Runtime behavior must stay aligned with:

- Task graph, not fixed swarm  
- Dynamic spawn policy + budgets  
- Permission barrier on tools  
- Compact context packs  

## One-line summary for a new chat

> Continue **claude-code-replica** (Streamlit multi-agent coding workspace). Repo `AdnanRaza88/claude-code-replica`. Runtime is hierarchical **TaskGraph + AgentRuntime** with thin keyword planner (7 domains), permission harness, and OpenAI-compatible providers (Zen/OpenCode fixed). Do not build 50 fixed agents; extend domain coverage, LLM planner, verification, and graph quality while keeping budgets, single-provider session, and permission gates.
