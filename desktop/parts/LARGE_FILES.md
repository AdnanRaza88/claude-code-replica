# Large files

`desktop/launch_engine.py` and `desktop/pack_portable.py` exceed the GitHub contents API batch size used by hourly automation.

Reassemble on a clone:

```
python desktop/parts/join_large_files.py
```

Parts live under `desktop/parts/`.
See PARTS_INDEX.txt and PARTS_SHA256.txt.

Hourly 2026-09-13 07:13 PKT: pushing launch_engine.py.part03-07.
app.py on GitHub remains full (SHA 57e524ef, 655 lines). Phase 4 exit still needs a Windows host.
