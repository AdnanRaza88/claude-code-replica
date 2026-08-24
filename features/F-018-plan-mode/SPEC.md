# F-018 — Plan mode

**Status:** todo  
**Phase:** A2 — build this next  

## Description

Runtime mode where the agent produces a structured plan and specs **without** executing write/edit/bash (read/search/web allowed). User approves, then switches to agent mode to execute.

## Why

Beginners and SDD need “think first.” Prevents parallel agents coding before contracts exist.

## Tech

- Session or run flag: `mode: plan | agent`  
- In plan mode, tool allowlist = read, search, web_search, web_fetch, github(read)  
- Output: markdown plan + optional task list JSON  
- Engine only; Streamlit/CLI only toggles the flag  

## Do

- Clear message when a write tool is blocked in plan mode  
- Persist last plan on session  

## Don’t

- Put mode logic only in Streamlit widgets  
- Allow bash “for exploration” that mutates state  

## Touch

- `src/orchestration/runtime.py`  
- `src/services/permission_service.py` or tool filter in runtime  
- `src/models/` if mode on session  
- Optional: `app.py` mode select (already has agent/plan select — wire for real)

## Done when

- Plan mode cannot write files  
- Agent mode unchanged  
- One automated or manual test documented  

## Done note

_(empty until verified)_
