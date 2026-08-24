# Docs index — Claude Code Replica

Planning and product docs live here so any chat (any account) can open the GitHub repo and recover the plan without full code context.

| Doc | Purpose |
|-----|---------|
| [VISION.md](VISION.md) | What we are building (beginner voice → specs → parallel build → safe review) |
| [BUILD_SEQUENCE.md](BUILD_SEQUENCE.md) | Ordered feature sequence; what to implement next |
| [PARALLEL_COHERENCE.md](PARALLEL_COHERENCE.md) | How parallel agents stay on one theme (no night-sky vs day-map) |
| [REVIEW_AND_FIX.md](REVIEW_AND_FIX.md) | Large-codebase review swarms; find vs fix; Mythos-style risk |
| [VOICE_AND_SDD.md](VOICE_AND_SDD.md) | Voice for beginners + spec-driven development flow |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Headless engine, surfaces (CLI / web / Docker / desktop later) |

**Features (implementation packets):** `../features/F-xxx-*/SPEC.md`  
**Flat checklist:** `../FEATURES.md`

**Rule for implement chats:** load only one `features/F-xxx-*/SPEC.md` + listed Touch files. Do not load the whole repo.
