# Large files not yet whole on GitHub

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed a comfortable single `push_files` payload.

Split copies live under `desktop/parts/`:

- `launch_engine.py.part01`–`part25` (on main, full sizes)
- `pack_portable.py.part01`–`part03` on main (part02 7998, part03 7974 — restore to 8000 if join fails)
- `pack_portable.py.part20` on main
- `pack_portable.py.part04`–`part19` still local-only (each 8000 except last)

Join on a machine with the tree:

```
python desktop/parts/join_large_files.py
```

That writes `desktop/parts/launch_engine.py` and `desktop/parts/pack_portable.py`. Copy those over the canonical `desktop/` files after hash check (`PARTS_SHA256.txt`).

## 2026-09-16 05:24 PKT

- GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER. Local match.
- Join + pack_min + launch_min tests: 7 passed.
- Next payload: pack_portable.py.part04–part07 (local 8000 each).
- Full launch_engine.py / pack_portable.py still local-only.
- Phase 4 exit still needs a Windows host.
