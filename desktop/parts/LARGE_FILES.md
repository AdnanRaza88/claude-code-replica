# Large files (join from parts)

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed the GitHub connector batch size.

Split into 8KB slices under `desktop/parts/`:

- `launch_engine.py.part01`–`part25` (on remote)
- `pack_portable.py.part01`–`part20` (part01 local+remote; part03 remote still 799 vs local 8000; part04–19 local backlog)

Join: `python desktop/parts/join_large_files.py`

Hourly 2026-09-15 22:05 PKT: GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER. Join+pack+launch min tests 7 passed. create_or_update_file on part03 did not grow past 799 (connector still writes short body). Next run retry pack part03–10 via push_files with full 8000-byte bodies.
