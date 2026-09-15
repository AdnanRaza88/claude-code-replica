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

Hourly automation 2026-09-15 08:01 PKT: GitHub app.py SHA 57e524ef still full (655 lines / 26092 bytes), no PLACEHOLDER. Join + pack min tests 4 passed. Restoring pack_portable.py.part03 to local 8000-byte slice (remote was truncated) plus part04 and part05. Backlog: launch_engine.py, pack_portable.py, pack parts 06-19. Phase 4 exit still needs a Windows host.
