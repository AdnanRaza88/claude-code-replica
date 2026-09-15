# Large files not yet whole on GitHub

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed a comfortable single `push_files` payload.

Split copies live under `desktop/parts/`:

- `launch_engine.py.part01`–`part25` (on main)
- `pack_portable.py.part01`–`part20` (01–03 + 20 on main; 04–19 backlog)

Join on a machine with the tree:

```
python desktop/parts/join_large_files.py
```

That writes `desktop/parts/launch_engine.py` and `desktop/parts/pack_portable.py`. Copy those over the canonical `desktop/` files after hash check (`PARTS_SHA256.txt`).

## 2026-09-15 10:16 PKT

- GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER.
- Join + pack_min + launch_min tests 7 passed.
- Remote pack_portable.py.part03 still 7833 vs local 8000.
- This run pushes pack parts 04–05 (8000 bytes each, not yet on main).
- Full launch_engine.py / pack_portable.py still local-only.
- Phase 4 exit still needs a Windows host.
