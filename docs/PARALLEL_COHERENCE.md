# Parallel coherence (theme / contract matching)

## Problem (game example)

User asked for a game. Parallel agents built faster, but:

- Sky agent → dark night sky  
- Map / props agents → daytime assumptions  
- Weapons / enemies → inconsistent style  

Root cause: agents shared the **task title** but not a **single locked design contract**. Parallelism without a shared source of truth produces mismatch.

## Solution in this system

### 1. Shared Project Bible (required before parallel code)

Before spawn of implementation children, orchestrator (or spec phase) writes a short immutable (until user changes) document:

- Theme (day/night, art style, tone)
- Constraints (tech stack, file layout, APIs)
- Naming conventions
- Non-goals
- Acceptance checks

Stored as session/project artifact, e.g. `.agentforge/BIBLE.md` or in-memory `SharedContext` attached to every child pack.

### 2. Every child gets the same bible slice

`ContextService.build_pack` must inject:

- Full or hashed bible summary
- Only the **slice** of specs relevant to that domain  
Not the entire codebase.

### 3. Parallel vs sequence decision

| Pattern | When |
|---------|------|
| **Parallel** | Tasks have no file/API dependency; bible already locked |
| **Sequence** | Task B needs Task A’s interface or generated paths |
| **Barrier** | Parallel group finishes → integrator checks bible + contracts → then next wave |

Planner/runtime must support **waves**: parallel set → barrier verify → next parallel set.

### 4. Integrator role

After parallel children return:

- Diff outputs against bible (theme keywords, agreed paths)
- Flag contradictions explicitly (“sky=night vs map=day”)
- Do not silently merge conflicting assets

### 5. What not to do

- Spawn N implementation agents with only the user one-liner as context
- Let each agent invent its own theme
- Assume “faster parallel” always beats a 10-line shared contract

## Feature packets

- `features/F-031-shared-context/SPEC.md` — SharedContext / bible injection  
- Ties to F-013 task graph, F-033 spec-driven, F-016 harness
