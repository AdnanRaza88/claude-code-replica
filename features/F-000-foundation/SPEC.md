# F-000 — Foundation / headless boundaries

**Status:** partial  

## Description

Keep tools, runtime, planner, services free of Streamlit/UI imports so CLI/web/desktop can share one engine.

## Do

- New logic in `src/` not only in `app.py`  
- Cross-platform paths  

## Don’t

- `import streamlit` inside tools or runtime  

## Touch

- entire `src/` when adding features  

## Done note

Ongoing constraint for all features.
