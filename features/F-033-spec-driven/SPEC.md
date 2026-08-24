# F-033 — Spec-driven pipeline

**Status:** done (engine + skills)  
**Phase:** B1  

## Description

Before implementation agents run, produce Intent → PRD-lite → TRD-lite → task waves. User can confirm. Then lock bible and execute.

## Tech

- Plan mode produces artifacts under `.agentforge/specs/`  
- Orchestrator refuses parallel code spawn until specs+bible exist (configurable strictness)  

## Do

- Keep docs short (not 50-page PRDs)  
- Link tasks to acceptance lines  

## Don’t

- Generate novels; generate contracts  

## See also

- `docs/VOICE_AND_SDD.md`  

## Touch

- `src/services/spec_service.py`  
- `src/orchestration/planner.py`  
- `src/orchestration/plan_mode_hooks.py`  
- `skills/sdd/`, `skills/planning/`, `skills/orchestrator/`  

## Done note

SpecService templates + lock gate; Planner plan/strict SDD routing to planning+sdd skill; plan mode allows write only under .agentforge/specs; skills teach contract-first agentic coding.
