from pathlib import Path
import sys

root = Path(__file__).resolve().parent

def join(stem: str) -> Path:
    parts = sorted(root.glob(f"{stem}.part*"))
    if not parts:
        raise SystemExit(f"no parts for {stem}")
    out = root / stem
    out.write_text("".join(p.read_text() for p in parts))
    print(f"wrote {out} from {len(parts)} parts ({out.stat().st_size} bytes)")
    return out

if __name__ == "__main__":
    targets = sys.argv[1:] or ["launch_engine.py", "pack_portable.py"]
    for t in targets:
        join(t)
