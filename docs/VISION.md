# Product vision

## Who it is for

Beginners with **no tech background**. They speak (or type) a simple problem in plain language. The system turns that into specs, then builds, then reviews — without requiring the user to know git, terminals, or frameworks.

## End-to-end flow (target)

1. **Input** — Voice or text. User describes what they want in everyday language.
2. **Understand** — Orchestrator clarifies only if needed; otherwise drafts intent.
3. **Spec-driven** — System writes short PRD / TRD / task specs **before** heavy coding.
4. **Shared bible** — One locked project context (theme, constraints, APIs, naming) that every agent reads.
5. **Parallel build** — Specialist agents work **in parallel** when independent; sequence only when there is a real dependency.
6. **Integrate + verify** — Merge results against the shared bible; run checks.
7. **Review swarm** — Separate find-bugs path; fix only with tight scope and verification (avoid “100 new bugs”).
8. **Surfaces** — Same engine behind CLI, web UI, Docker; Streamlit is temporary; desktop last.

## Non-goals (for now)

- Full Claude Code parity on day one
- Unbounded agent spawn without token/permission checks
- Silent auto-fix of the whole repo
- Requiring PinchTab / local browser for basic use

## Success criteria

- Beginner can go from spoken idea → working artifact with minimal settings.
- Parallel agents do not contradict theme or contracts.
- Large repos are reviewed in chunks with user consent when many sub-agents are needed.
- Find-bugs and fix-bugs are separate, controlled phases.
