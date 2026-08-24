# F-034 — Review swarm (find-only)

**Status:** todo  
**Phase:** C1  

## Description

For large codebases, a review lead estimates context needs, proposes N read-only explorer sub-agents, asks user permission if N is high, then map-reduces findings. **No auto-fix in this feature.**

## Tech

- Size heuristics (files, LOC)  
- Context budget math from model config  
- Spawn only with `allowed_tools` read/search  
- Structured findings JSON merge  

## Do

- Explicit user prompt when N > threshold  
- A-grade coverage language vs D-grade skim  

## Don’t

- Claim full-repo review in one context window  
- Write/edit during find phase  

## See also

- `docs/REVIEW_AND_FIX.md`  

## Touch

- `src/orchestration/runtime.py`  
- `src/harness/`  
- `src/services/permission_service.py`  
- `skills/code-review/`  

## Done note

_(empty)_
