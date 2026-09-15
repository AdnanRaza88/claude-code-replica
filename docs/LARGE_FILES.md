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
- This run logged pack parts 04–05 still local (8000 bytes); remote part03 7833.
- Full launch_engine.py / pack_portable.py still local-only.
- Phase 4 exit still needs a Windows host.

## 2026-09-15 11:10 PKT

- GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER.
- Join + pack_min + launch_min tests 7 passed.
- Restoring pack_portable.py.part03 to local 8000 bytes and pushing part03-part05.
- Phase 4 exit still needs Windows host.

## 2026-09-15 12:16 PKT

- GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER.
- Join + pack_min + launch_min tests 7 passed.
- Local pack_portable.py.part03–part05 each 8000 bytes, no PLACEHOLDER.
- Remote part03 still short vs local 8000; full launch_engine.py / pack_portable.py still local-only.
- Phase 4 exit still needs a Windows host.

## 2026-09-15 13:18 PKT

- GitHub app.py SHA 57e524ef full 655 lines / 26092 bytes, no PLACEHOLDER.
- Join + pack_min + launch_min tests 7 passed.
- Local pack_portable.py.part03–part09 each 8000 bytes, no PLACEHOLDER.
- Accidental short push then partial restore left remote part03 at 799 bytes (d1e74477). Next run must overwrite with exact local 8000-byte slice.
- Full launch_engine.py / pack_portable.py still local-only.
- Phase 4 exit still needs a Windows host.
