# Claude Code Replica — Feature Roadmap

**Canonical planning:** `docs/` (vision, sequence, coherence, review, voice).  
**Per-feature packets:** `features/F-xxx-*/SPEC.md` — load **only** that SPEC in implement chats.  
This file remains a flat index; detailed Do/Don’t live in each SPEC.

**Next to build:** **F-018 Plan mode** → F-020 → F-031 (see `docs/BUILD_SEQUENCE.md`).

---

## How to implement (one feature per chat)

```
Feature: F-xxx — <name>
Read only: features/F-xxx-*/SPEC.md and docs pages it links
Follow Do/Don’t. Engine first, UI last.
Do not refactor unrelated code. Do not expand Streamlit dependency.
When done: mark status done + one-line Done note in that SPEC.md
```

Do not reload the whole repo into context.

---

## Architecture rules

- Business logic in **headless engine** (`src/tools`, `src/orchestration`, `src/services`, `src/harness`).
- UI adapters only: Streamlit temporary → CLI → Web+Docker → Desktop last.
- Cross-platform pathlib; no secrets in repo.
- Parallel agents share a **Project Bible** (`docs/PARALLEL_COHERENCE.md`).
- Find bugs ≠ auto-fix (`docs/REVIEW_AND_FIX.md`).

---

## Docs map

| Doc | Purpose |
|-----|---------|
| `docs/VISION.md` | Beginner voice → specs → parallel build → safe review |
| `docs/BUILD_SEQUENCE.md` | Ordered phases A–D; next feature |
| `docs/PARALLEL_COHERENCE.md` | Night-sky vs day-map problem + bible |
| `docs/REVIEW_AND_FIX.md` | Review swarm, token gates, safe fix |
| `docs/VOICE_AND_SDD.md` | Voice + spec-driven flow |
| `docs/ARCHITECTURE.md` | Engine vs surfaces |

---

## Feature packets (folders)

| ID | Folder | Status |
|----|--------|--------|
| F-000 | `features/F-000-foundation/` | partial |
| F-018 | `features/F-018-plan-mode/` | **todo — build next** |
| F-020 | `features/F-020-project-memory/` | todo |
| F-023 | `features/F-023-cli/` | todo |
| F-024 | `features/F-024-web-ui/` | todo |
| F-025 | `features/F-025-docker/` | todo |
| F-031 | `features/F-031-shared-context/` | todo |
| F-032 | `features/F-032-voice-input/` | todo |
| F-033 | `features/F-033-spec-driven/` | todo |
| F-034 | `features/F-034-review-swarm/` | todo |
| F-035 | `features/F-035-safe-fix/` | todo |

Older checklist items (tools, web, providers, permissions, skills, harness) remain partially implemented in `src/`; harden when a SPEC requires it.

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-08-24 | Streamlit temporary; CLI + web + Docker; desktop last (Tauri) |
| 2026-08-24 | One feature per chat; docs/ + features/*/SPEC.md source of truth |
| 2026-08-24 | Parallel agents must share Project Bible |
| 2026-08-24 | Find vs safe-fix separated; review swarm asks permission if N high |
| 2026-08-24 | Voice + SDD for beginners |
| 2026-08-24 | **Next implement chat: F-018 Plan mode** |
