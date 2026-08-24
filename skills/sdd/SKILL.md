---
name: sdd
domain: planning
description: Spec-driven + agentic coding — Intent, PRD-lite, TRD-lite, waves, bible; contracts not novels; gate code until locked
allowed_tools: read, search, web_search, write, edit
priority: 95
version: 1.0
---

# Spec-driven + agentic coding

You write **contracts** first, then code. You are not a vibe coder.

## Pipeline (always this order)

1. **Intent** — 5–10 lines: what / who / success / out of scope
2. **PRD-lite** — goals, non-goals, acceptance checkboxes (testable)
3. **TRD-lite** — stack, modules, interfaces, deps, risks
4. **WAVES** — wave 0 lock → sequential foundation → parallel slices → verify barrier
5. **BIBLE** — one theme, stack, naming, layout, non-goals, parallel rules
6. User confirm → **lock** → only then implementation agents

Artifacts live under `.agentforge/specs/<slug>/` as `INTENT.md`, `PRD.md`, `TRD.md`, `WAVES.md`, `BIBLE.md` plus `STATUS.json`.

## Good practices

- Short: prefer one screen per doc. Contracts beat essays.
- Every implementation task maps to at least one **acceptance** line in PRD.
- Parallel only when tasks share **no** file or API ownership conflict.
- Bible is the single theme/stack source of truth; children do not invent a second theme.
- Non-goals are mandatory — they prevent scope creep and vibe features.
- Prefer explicit interfaces (inputs → outputs) over vague "handle X".
- Wave barrier: do not start wave N+1 until wave N acceptance is checked.

## Plan mode behavior

When session is plan mode or user asks for a plan/spec:

- Produce or fill the five artifacts.
- Do not implement production features yet.
- Ask user to confirm acceptance lines before lock.

## Agent mode / implementation

- Refuse large parallel code spawn if specs are missing or unlocked (say what is missing).
- After lock, follow bible + TRD interfaces exactly.
- If reality contradicts bible, stop and surface the contradiction — do not silently diverge.

## Result shape for spec phase

```json
{
  "status": "success|partial",
  "summary": "what was specified",
  "artifacts": [".agentforge/specs/<slug>/..."],
  "open_questions": [],
  "plan": { "slug": "...", "next": "confirm and lock" }
}
```

## Anti-patterns

- 50-page PRDs
- Code before acceptance criteria
- Parallel agents with only a one-line user ask and no bible
- Each agent choosing its own stack or visual theme
