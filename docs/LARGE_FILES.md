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

Hourly automation 2026-09-14 09:04 PKT: GitHub app.py SHA 57e524ef still full (655 lines / 26092 bytes), no PLACEHOLDER. Pushed launch_engine.py.part25 (full tail through `if __name__`) and a first slice of part23 (commit e99c327). part23 on remote is still short versus local 8000 bytes; part24 not on remote yet. Backlog remains launch_engine.py, pack_portable.py, part23 restore, part24, pack_portable 01-19. Phase 4 exit still needs a Windows host.
