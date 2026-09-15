# Large files (join from parts)

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed the GitHub connector batch size.

Split into 8KB slices under `desktop/parts/`:

- `launch_engine.py.part01`–`part25` (on remote)
- `pack_portable.py.part01`–`part20` (part01–03 + part20 on remote; part04–19 local backlog)

Join: `python desktop/parts/join_large_files.py`

Hourly 2026-09-15 06:04 PKT: GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER. Join + pack tests 6 passed. Restoring pack_portable parts 04+.
