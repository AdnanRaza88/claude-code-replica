# F-020 — Project memory (CLAUDE.md-style)

**Status:** done  
**Phase:** A3  

## Description

Load project instruction files (`CLAUDE.md`, `AGENTS.md`, or `.agentforge/memory.md`) into every agent context pack.

## Tech

- `ContextService` reads file if present under project root  
- Cap size (e.g. 8–16k chars)  
- Optional later: `/init` generator  

## Do / Don’t

- Do: missing file = no error, empty memory  
- Don’t: overwrite user memory without ask  

## Touch

- `src/services/context_service.py`  
- `src/models/context.py`  
- Session `project_root`  

## Done note

Engine: ContextService.load_project_memory + inject into ContextPack.to_prompt_block; first-hit CLAUDE.md → AGENTS.md → .agentforge/memory.md; 12k cap; tests in tests/test_project_memory.py.
