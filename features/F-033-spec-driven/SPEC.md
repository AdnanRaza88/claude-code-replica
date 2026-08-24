# F-033 — Spec-driven pipeline

**Status:** todo  
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

- `src/orchestration/planner.py`  
- `src/orchestration/runtime.py`  
- plan mode F-018  

## Done note

_(empty)_
