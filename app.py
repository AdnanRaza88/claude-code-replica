from pathlib import Path
_dir = Path(__file__).resolve().parent
_code = "".join((_dir / f"_app_part_{i}.py").read_text() for i in range(4))
exec(compile(_code, str(Path(__file__).resolve()), "exec"), globals())
