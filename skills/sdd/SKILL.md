---
name: sdd
domain: planning
description: Spec-driven + agentic coding — interview, Intent/PRD/TRD/WAVES/BIBLE/PLAN, EARS, examples, gates; contracts not novels
allowed_tools: read, search, web_search, write, edit
priority: 95
version: 1.1
---

# Spec-driven + agentic coding

You write **contracts** first, then code. Not vibe coding.
Aligned with Agent Factory (spec → build → verify), GitHub Spec Kit, and Claude plan-first practice.

## Pipeline order (do not skip)

1. **Interview** (plan mode) — 3–7 hard questions; record Q/A in Intent
2. **Intent** — what/why, non-goals, open questions (no stack)
3. **PRD-lite** — goals, non-goals, EARS requirements, acceptance checkboxes, Given/When/Then examples, NFRs
4. **TRD-lite** — stack, modules, interfaces, data, deps, test mapping to ACs
5. **WAVES** — wave 0 lock → foundation → parallel slices → barriers → verify
6. **BIBLE** — one theme, stack, naming, parallel rules
7. User **confirm** → **lock** (no leftover `_fill_` placeholders)
8. **PLAN** — file-level implementation steps (after lock, before feature code)
9. Implementation agents → verify against ACs + examples

Paths: `.agentforge/specs/<slug>/{INTENT,PRD,TRD,WAVES,BIBLE,PLAN}.md` + `STATUS.json`

Status flow: `draft → clarified → confirmed → locked → in_progress → done`

## Interview rules (before filling templates)

Ask only non-obvious questions, for example:

- Who is the primary user and what is the single success metric?
- What must we explicitly NOT build this pass?
- Which edge cases will users hit in week one?
- What stack/constraints are fixed vs free?
- What does “done” look like as a test or demo?

If the user is silent on a point, list it under **Open questions** — do not invent product policy.

## Writing quality (Smart-kid test)

- Another engineer could implement from the docs without the chat history.
- Every sentence either **constrains** the build or **helps verify** it; delete padding.
- Prefer EARS: `WHEN [condition] THE SYSTEM SHALL [behavior]`.
- Ban vague words: fast, clean, intuitive, should — replace with measurable ACs.
- Examples beat adjectives: Given / When / Then.
- MECE: one requirement lives in one place; cross-link, do not duplicate.
- Balanced detail: not a one-liner, not a 50-page PRD.

## Plan mode

- Produce or refine the artifacts above.
- Write only under `.agentforge/specs/` and `.agentforge/BIBLE.md`.
- No production feature code. No bash.
- End with: open questions, path to confirm/lock, slug name.

## Agent mode / implementation

- If core specs missing or not locked → refuse large parallel code; say what is missing.
- After lock, follow bible + TRD interfaces; map tasks to ACn.
- Contradiction with bible → stop and surface; do not silent-merge.
- Prefer sequence when shared files/APIs; parallel only when WAVES says so.

## Result shape (spec phase)

```json
{
  "status": "success|partial",
  "summary": "what was specified",
  "artifacts": [".agentforge/specs/<slug>/..."],
  "open_questions": [],
  "plan": { "slug": "...", "status": "draft|clarified|...", "next": "confirm and lock" }
}
```

## Anti-patterns

- Jumping to code from a one-line ask
- Empty non-goals or empty open questions when ambiguous
- Parallel agents with no bible
- Each agent inventing stack or theme
- Confirm/lock while `_fill_` placeholders remain
