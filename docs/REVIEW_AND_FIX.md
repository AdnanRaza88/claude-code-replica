# Review vs fix (Mythos-style risk)

## Problem

Large models can **find** bugs well but **fix** them poorly: one fix introduces many new bugs. Anthropic’s Mythos-class messaging reflects that finding ≠ safe fixing.

## Policy in this system

### Separate phases

1. **FIND** — read-only exploration + report (locations, severity, evidence)  
2. **PRIORITIZE** — user or orchestrator picks what to fix  
3. **FIX** — small scoped patches only; one issue (or tight cluster) per wave  
4. **VERIFY** — tests / grep / harness checks before claiming done  

Never “review entire monorepo and auto-fix everything” in one shot.

### Review swarm (dynamic sub-agents)

For large codebases the review lead must:

1. Estimate size (file count, LOC, dirs)  
2. Estimate **own context budget** (model window − system − bible − report template)  
3. Compute how many **read-only explorer** sub-agents are needed (by folder or module)  
4. **Ask the user** if spawn count is high, e.g.:

   > Codebase is large. My context cannot hold a full review at once.  
   > I need ~N review sub-agents for A-grade coverage (not D-grade skim).  
   > Approve spawn of N read-only explorers?

5. If local model / unlimited: still report cost in time/tokens; still prefer permission for N above threshold (config).

### Token / spawn gates (harness)

Before `spawn`:

- Check remaining token budget and child budget  
- Cap concurrent review children  
- Prefer map-reduce: each child returns structured findings JSON; lead merges  

### Fix agents

- May write/edit only under explicit fix task  
- Must not expand scope (“while here, rewrite module”)  
- Verification required (F-029) after each fix wave  

## Feature packets

- `features/F-034-review-swarm/SPEC.md`  
- `features/F-035-safe-fix/SPEC.md`  
- Related: F-012 permissions, F-013 spawn budgets, F-027 code-review skill
