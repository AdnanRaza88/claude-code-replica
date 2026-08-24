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
       else leaf → **CognitiveLoop harness** (Think→Reason→Act→Observe→Verify)
                   fallback: legacy single-shot provider.invoke + tools
  → PermissionService on every tool call
  → EventService (created/started/thinking/reasoning/tool_*/completed/failed)
  → UI: chat + agent tree + events + permission panel
```

### Key modules

| Path | Role |
|------|------|
| `app.py` | Streamlit shell, credentials, model picker, chat, tree |
| `src/orchestration/planner.py` | Domain keywords, graph build |
| `src/orchestration/runtime.py` | Spawn, execute, children, tools, cancel; leaf path prefers harness |
| `src/harness/` | Per-agent isolated cognitive sandbox + CognitiveLoop |
| `src/harness/sandbox.py` | `AgentSandbox`, `SandboxRegistry` (no shared state across agents) |
| `src/harness/loop.py` | Think → Reason → Act → Observe → Verify loop |
| `src/harness/types.py` | `Phase`, `StepKind`, `SandboxStep`, `SandboxTrace` |
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

### Planner domains + skills (current)

Domains: `orchestrator`, `research`, `implementation`, `code-review`, `testing`, `git`, `frontend`, `backend`, `security`, `docs`, `browser`, `tools`, `memory`, `planning`, `general`.

Each domain has a primary skill under `skills/<domain>/SKILL.md` (Claude-style frontmatter + body).  
`SkillService` loads them; `ContextService` injects skill body into each agent's system pack; planner assigns `required_skills` + domain tool allowlists.

Simple prompts → one domain agent. Multi-keyword / long objectives → root **orchestrator** + specialist children, each with isolated context + own skill.

## Providers (important)

- Single provider/model per session; all agents inherit it.
- **OpenCode Zen** base: `https://opencode.ai/zen/v1`

## Harness (2026-08-24)

Per-agent isolated cognitive sandbox inspired by DeepSeek Harness scoped context:
- `AgentSandbox` — private trace, scratch, notes, tool allowlist (never shared across agents)
- `CognitiveLoop` — Think → Reason → Act → Observe → Verify with step budget (max 8)
- Leaf agents use harness by default; on any harness error, runtime falls back to legacy `_run_leaf`
- Events: THINKING / REASONING / TOOL_* / SOURCE_FOUND / COMPLETED remain compatible with Streamlit UI
