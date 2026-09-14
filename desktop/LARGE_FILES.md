# Large files

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed the GitHub contents API size that hourly automation can push in one blob.

They are split under `desktop/parts/`:

- `launch_engine.py.part01` … `launch_engine.py.part25`
- `pack_portable.py.part01` … `pack_portable.py.part20`

Join on a clone:

```
python desktop/parts/join_large_files.py
```

Hourly 2026-09-14 06:08 PKT: parts 20-25 of launch_engine staged for GitHub. Full `app.py` on main remains SHA 57e524ef (655 lines, no PLACEHOLDER).

Do not replace `app.py` with PLACEHOLDER.
