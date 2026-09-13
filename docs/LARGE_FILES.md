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

Hourly automation 2026-09-13 08:03 PKT: GitHub `app.py` SHA 57e524ef still full (655 lines / 26092 bytes). Remote parts were part01–03 + pack part20 + index/join. This run pushes launch_engine.py.part04–06. Next: part07–25 then pack_portable.py.part01–19.
