# Claude Code Replica — project memory

- Prefer pathlib; no hardcoded OS paths.
- Business logic stays in src/ (engine); app.py is a temporary Streamlit adapter.
- Plan mode (session.mode=plan): no write/edit/bash — read/search/web/github only.
- One feature per focused change when possible; follow features/*/SPEC.md Do/Don't.
- Do not put secrets in the repo.
