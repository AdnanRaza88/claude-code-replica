# Build sequence

Implement **one feature per chat**. Mark SPEC status when verified. Only then start the next in a **new chat**.

## Phase A — Foundation lock (current codebase)

| Order | ID | Name | Status | Why this order |
|------|-----|------|--------|----------------|
| A1 | F-000 | Foundation / headless boundaries | partial | Ensure tools/runtime stay UI-free |
| A2 | F-018 | Plan mode | todo | Specs before code; needed for SDD |
| A3 | F-020 | Project memory (CLAUDE.md-style) | todo | Stable project instructions |
| A4 | F-031 | Shared context / bible | todo | Unlocks safe parallel build |

## Phase B — Coherent parallel build

| Order | ID | Name | Status |
|------|-----|------|--------|
| B1 | F-033 | Spec-driven pipeline (PRD/TRD-lite) | todo |
| B2 | F-013 | Task graph waves + barriers | partial |
| B3 | F-016 | Harness verify barriers | partial |

## Phase C — Safe quality

| Order | ID | Name | Status |
|------|-----|------|--------|
| C1 | F-034 | Review swarm (find-only) | todo |
| C2 | F-035 | Safe fix waves | todo |
| C3 | F-029 | Structured verification | todo |

## Phase D — Beginner access

| Order | ID | Name | Status |
|------|-----|------|--------|
| D1 | F-032 | Voice input adapter | todo |
| D2 | F-023 | Terminal CLI | todo |
| D3 | F-024 | Web UI (replace Streamlit) | todo |
| D4 | F-025 | Docker image | todo |
| D5 | F-026 | Desktop shell | todo (last) |

## Already partial (harden only when needed)

F-001–F-005 tools, F-008–F-009 web, F-011 providers, F-012 permissions, F-014 skills, F-027/F-028 domain skills.

## Next feature to build (recommendation)

**Start next chat with: F-018 Plan mode**

Reason: enables SDD, reduces reckless writes, prerequisite for bible + parallel waves + beginner “describe then build” flow. After F-018 is verified → F-020 → F-031.
