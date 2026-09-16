# Large files not yet whole on GitHub

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed a comfortable single `push_files` payload.

Split copies live under `desktop/parts/`:

- `launch_engine.py.part01`-`part25` (on main, full sizes)
- `pack_portable.py.part01`-`part03` on main (part02 7998, part03 7974)
- `pack_portable.py.part20` on main
- `pack_portable.py.part04`-`part19` still local-only until a full 8000-byte slice lands

## 2026-09-16 21:23 PKT

- GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER. Local match.
- Join + pack_min + launch_min tests: 7 passed.
- This run payload: LARGE_FILES + VERSION 0.5.56 + run 20260916-2123. Pack part04-07 kept local.
- Remaining backlog: launch_engine.py, pack_portable.py, pack parts 04-19.
- Phase 4 exit still needs a Windows host.

Join on a machine with the tree:

```
python desktop/parts/join_large_files.py
```
