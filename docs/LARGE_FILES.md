# Large files not yet whole on GitHub

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed a comfortable single `push_files` payload.

Split copies live under `desktop/parts/`:

- `launch_engine.py.part01`–`part25`
- `pack_portable.py.part01`–`part20`

Join on a machine with the tree:

```
python desktop/parts/join_large_files.py
```

That writes `desktop/parts/launch_engine.py` and `desktop/parts/pack_portable.py`. Copy those over the canonical `desktop/` files after hash check (`PARTS_SHA256.txt`).

Hourly automation 2026-09-15 02:06 PKT: GitHub app.py SHA 57e524ef still full (655 lines / 26092 bytes), no PLACEHOLDER. Local pack_portable.py.part03–10 are 8000 bytes each with no SEE_FILE. Remote pack_portable.py.part03 is still SEE_FILE (SHA ae5f666d) — restore next run via push_files. Backlog: launch_engine.py, pack_portable.py, pack parts 03-19. Phase 4 exit still needs a Windows host.
