from pathlib import Path
import hashlib
import sys

root = Path(__file__).resolve().parent


def expected_hashes() -> dict[str, tuple[str, int]]:
    path = root / "PARTS_SHA256.txt"
    found: dict[str, tuple[str, int]] = {}
    if not path.is_file():
        return found
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        bits = line.split()
        if len(bits) >= 3 and len(bits[0]) == 64:
            found[bits[1]] = (bits[0], int(bits[2]))
    return found


def join(stem: str) -> Path:
    parts = sorted(root.glob(f"{stem}.part*"))
    if not parts:
        raise SystemExit(f"no parts for {stem}")
    expect = expected_hashes()
    chunks: list[str] = []
    for part in parts:
        data = part.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        spec = expect.get(part.name)
        if spec and (digest != spec[0] or len(data) != spec[1]):
            raise SystemExit(
                f"hash mismatch {part.name}: got {digest} {len(data)} want {spec[0]} {spec[1]}"
            )
        chunks.append(data.decode("utf-8"))
    out = root / stem
    out.write_text("".join(chunks), encoding="utf-8")
    print(f"wrote {out} from {len(parts)} parts ({out.stat().st_size} bytes)")
    return out


if __name__ == "__main__":
    targets = sys.argv[1:] or ["launch_engine.py", "pack_portable.py"]
    for t in targets:
        join(t)
