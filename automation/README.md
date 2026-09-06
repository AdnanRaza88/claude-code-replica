# Automation runner (hourly cadence, Asia/Karachi)

**Standing orders:** `AUTOMATION_INSTRUCTIONS.md` (read first every run)
**State:** `state.json`
**Phases:** `docs/DESKTOP_BUILD_PHASES.md`
**Structure map:** `STRUCTURE.md`

Each Grok automation run:

1. Reads AUTOMATION_INSTRUCTIONS then state then phases then STRUCTURE
2. Does 1-3 tasks for the current phase only
3. Any new MCP / MCP-like tools must get CRUD tests
4. Updates state.json + log under runs/
