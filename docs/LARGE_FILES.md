# Large files not yet whole on GitHub

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed a comfortable single `push_files` payload.

Split copies live under `desktop/parts/`:

- `launch_engine.py.part01`–`part25` (on main, full sizes)
- `pack_portable.py.part01` (8000), `part02` (7998), `part03` remote 799 vs local 8000 (restore when sandbox has the local slice), `part20` (on main)
- `pack_portable.py.part04`–`part19` still local-only (each 8000 except last)

Join on a machine with the tree:

```
python desktop/parts/join_large_files.py
```

That writes `desktop/parts/launch_engine.py` and `desktop/parts/pack_portable.py`. Copy those over the canonical `desktop/` files after hash check (`PARTS_SHA256.txt`).

## 2026-09-15 20:11 PKT

- GitHub app.py SHA 57e524ef full ~26k, AgentForge branded Streamlit check UI, no PLACEHOLDER.
- This hourly runner could not open the local sandbox (HADES_NO_CAPACITY), so pack_portable.py.part03 was not restored this run.
- Host launchers already on main under desktop/windows (Accept through Host*).
- VERSION 0.5.56. Phase 4 exit still needs a Windows host.

## 2026-09-15 19:28 PKT

- GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER. Local match.
- Join + pack_min + launch_min tests 7 passed.
- Local pack_portable.py.part03–part07 each 8000 bytes, no PLACEHOLDER/SEE_FILE.
- Full launch_engine.py / pack_portable.py still local-only.
- Phase 4 exit still needs a Windows host.
