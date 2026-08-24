# F-033 — Spec-driven pipeline

**Status:** done (engine + skills + P0/P1 quality)  
**Phase:** B1  

## Description

Before implementation agents run, produce Intent → PRD-lite → TRD-lite → task waves. User can confirm. Then lock bible and execute.

## Tech

- Plan mode produces artifacts under `.agentforge/specs/`  
- Orchestrator refuses parallel code spawn until specs+bible exist (configurable strictness)  
- Templates include EARS, Given/When/Then examples, PLAN post-lock, placeholder gate on confirm/lock  

## Do

- Keep docs short (not 50-page PRDs)  
- Link tasks to acceptance lines  
- Interview before inventing product policy  

## Don’t

- Generate novels; generate contracts  
- Lock while `_fill_` placeholders remain  

## See also

- `docs/VOICE_AND_SDD.md`  

## Touch

- `src/services/spec_service.py`  
- `src/orchestration/planner.py`  
- `src/orchestration/plan_mode_hooks.py`  
- `skills/sdd/`, `skills/planning/`, `skills/orchestrator/`  

## Done note

P0/P1: richer templates (EARS, examples, NFRs, PLAN), status clarified→…→done, placeholder_report blocks confirm/lock, sdd skill interview loop + Smart-kid rules.
