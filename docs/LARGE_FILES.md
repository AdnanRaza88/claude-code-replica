# Large files not yet whole on GitHub

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed a comfortable single `push_files` payload.

Split copies live under `desktop/parts/`:

- `launch_engine.py.part01`–`part25` (on GitHub, 8000-byte slices; part25 tail 6132)
- `pack_portable.py.part01`–`part20` (part01 and part20 on GitHub; part02/03 currently SEE_FILE after 5becdac9 — restore 8000-byte local files next; part04–19 still local)

Join on a machine with the tree:

```
python desktop/parts/join_large_files.py
```

That writes `desktop/parts/launch_engine.py` and `desktop/parts/pack_portable.py`. Copy those over the canonical `desktop/` files after hash check (`PARTS_SHA256.txt`).

Hourly automation 2026-09-14 13:04 PKT: GitHub app.py SHA 57e524ef still full (655 lines / 26092 bytes), no PLACEHOLDER. Join tests 3 passed. Phase 4 exit still needs a Windows host.
