# Large files not yet whole on GitHub

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed a comfortable single `push_files` payload.

Split copies live under `desktop/parts/`:

- `launch_engine.py.part01`–`part25` (on main, full sizes)
- `pack_portable.py.part01`–`part03` on main (verify 8000 bytes)
- `pack_portable.py.part20` on main
- `pack_portable.py.part04`–`part19` still local-only (each 8000 except last)

Join on a machine with the tree:

```
python desktop/parts/join_large_files.py
```

## 2026-09-16 04:04 PKT

- GitHub app.py SHA 57e524ef full 655 lines, no PLACEHOLDER.
- Join + pack_min + launch_min tests 9 passed.
- Phase 4 exit still needs a Windows host.
