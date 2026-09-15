# Large files not yet whole on GitHub

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed a comfortable single `push_files` payload.

Split copies live under `desktop/parts/`:

- `launch_engine.py.part01`–`part25` (on main, full sizes)
- `pack_portable.py.part01` (8000), `part02` (~8000), `part03` local 8000 (remote still short), `part20` (on main)
- `pack_portable.py.part04`–`part19` still local-only (each 8000 except last)

Join on a machine with the tree:

```
python desktop/parts/join_large_files.py
```

That writes `desktop/parts/launch_engine.py` and `desktop/parts/pack_portable.py`. Copy those over the canonical `desktop/` files after hash check (`PARTS_SHA256.txt`).

## 2026-09-16 01:06 PKT

- GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER. Local match.
- Join + pack_min + launch_min tests 7 passed.
- Remote pack_portable.py.part03 still short vs local 8000 (SHA 760e5510).
- pack parts 04–19 still local-only. Full launch_engine.py / pack_portable.py still local-only.
- Phase 4 exit still needs a Windows host.
