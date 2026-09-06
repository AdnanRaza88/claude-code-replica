# Automation runner (hourly cadence, Asia/Karachi)

**Standing orders:** `AUTOMATION_INSTRUCTIONS.md` (read first every run)
**State:** `state.json`
**Phases:** `docs/DESKTOP_BUILD_PHASES.md`
**Structure map:** `STRUCTURE.md`

Each Grok automation run:

1. Reads AUTOMATION_INSTRUCTIONS → state → phases → STRUCTURE
2. Does 1–3 tasks for the **current phase only**
3. Any new MCP / MCP-like tools must get **CRUD tests** (Create/Read/Update/Delete) or documented read-only + full Read tests
4. **GitHub sync:** push 8–20 backlog files via `github___push_files` to `AdnanRaza88/claude-code-replica` main (see AUTOMATION_INSTRUCTIONS section 8)
5. Updates `state.json` + log under `runs/`

Do not skip phases. Prefer small, shippable changes.

Manual check:
```bash
cd /home/workdir/artifacts/claude-code-replica
python -c "import json; print(json.load(open('automation/state.json'))['current_phase'])"
uvicorn backend.main:app --reload --port 8765
pytest tests/ -q
```
