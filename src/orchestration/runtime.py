from __future__ import annotations

from pathlib import Path

_parts = Path(__file__).resolve().parent / "_runtime_parts"
_code = "".join((_parts / f"p{i}.txt").read_text(encoding="utf-8") for i in range(4))
exec(compile(_code, str(Path(__file__).resolve().parent / "runtime_impl.py"), "exec"), globals())
