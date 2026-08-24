# F-031 — Shared context / Project Bible

**Status:** done (load + inject)  
**Phase:** A4  

## Description

Single locked “bible” (theme, stack, constraints, naming) injected into every child agent pack so parallel work stays coherent.

## Tech

- Model: `SharedContext` or markdown artifact `.agentforge/BIBLE.md`  
- Written in plan/spec phase; versioned; children get full or summary  
- Integrator compares outputs to bible after parallel wave  

## Do

- Lock before parallel implementation spawn  
- Surface contradictions explicitly  

## Don’t

- Let each agent invent theme  
- Skip bible for “speed”  

## See also

- `docs/PARALLEL_COHERENCE.md`  

## Touch

- `src/services/context_service.py`  
- `src/models/context.py`  

## Done note

Load .agentforge/BIBLE.md or BIBLE.md into every pack; set_project_bible(force=) never silent-overwrites; full parallel integrator still future work.
