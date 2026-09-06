# AgentForge (AI Engineer OS) — Code Structure Map

**Product name:** AgentForge (AI Engineer OS)
**Former name:** Claude Code Replica
**Path:** claude-code-replica/ (rename target agentforge/)
**Purpose:** Single map of folders to services to tools. See full file in workspace for complete map.

## Tech stack
- FastAPI thin backend, logic in src/
- Liquid-glass frontend
- Tauri/Windows desktop pack under desktop/
- OpenCode + Gemini providers
- Automation: automation/AUTOMATION_INSTRUCTIONS.md

## Key folders
- backend/ — FastAPI
- src/ — orchestration, harness, tools, services
- frontend/ — liquid-glass UI
- desktop/ — Windows pack
- skills/ — domain skills
- automation/ — phase state + standing orders

Full detailed connection map is maintained in the local STRUCTURE.md (16073 bytes). This commit seeds the AgentForge identity on GitHub.
