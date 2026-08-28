from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


ENTRY_CHARS = 280
WAKE_LINES = 96
LOG_REC = 320
TREE_REC = 320


def _pad(text: str, width: int) -> bytes:
    raw = text.encode("utf-8")[: width - 1]
    return raw + b"\n" + b" " * (width - len(raw) - 1)


def _unpad(data: bytes) -> str:
    return data.split(b"\n", 1)[0].decode("utf-8", errors="replace").rstrip()


def _cover(T: int, alpha: float) -> list[tuple[int, int]]:
    root = 1
    while root < T:
        root *= 2
    out: list[tuple[int, int]] = []
    stack = [(0, root)]
    while stack:
        lo, hi = stack.pop()
        if lo >= T:
            continue
        size = hi - lo
        if size > 1 and (hi > T or size > alpha * (T - lo)):
            mid = (lo + hi) // 2
            stack.append((mid, hi))
            stack.append((lo, mid))
        else:
            out.append((lo, hi))
    out.sort()
    return out


def cover(T: int, budget: int) -> list[tuple[int, int]]:
    if T <= 0:
        return []
    if T <= budget:
        return [(i, i + 1) for i in range(T)]
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if len(_cover(T, mid)) > budget:
            lo = mid
        else:
            hi = mid
    out = _cover(T, hi)
    while len(out) < budget:
        i = max((i for i, b in enumerate(out) if b[1] - b[0] > 1), default=None)
        if i is None:
            break
        lo_, hi_ = out[i]
        mid = (lo_ + hi_) // 2
        out[i : i + 1] = [(lo_, mid), (mid, hi_)]
    return out


class OptMemStore:
    """Project-scoped permanent memory: append-only log + binary merge tree.

    Inspired by VictorTaelin/OptMem. Store lives under
    {project_root}/.agentforge/optmem/ so it travels with the repo.
    """

    def __init__(self, project_root: str | Path | None = None, memory_dir: str | Path | None = None):
        if memory_dir:
            self.root = Path(memory_dir)
        elif project_root:
            self.root = Path(project_root) / ".agentforge" / "optmem"
        else:
            self.root = Path.home() / ".agentforge" / "optmem" / "default"
        self.log_path = self.root / "LOG.txt"
        self.tree_dir = self.root / "TREE"

    def exists(self) -> bool:
        return self.root.is_dir() and self.log_path.is_file()

    def init(self) -> str:
        self.root.mkdir(parents=True, exist_ok=True)
        self.tree_dir.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_bytes(b"")
        return (
            f"OptMem initialized at {self.root}\n"
            f"Use memory_wake at session start, memory_note to record facts."
        )

    def count(self) -> int:
        if not self.log_path.exists():
            return 0
        return self.log_path.stat().st_size // LOG_REC

    def _read_entry(self, idx: int) -> str:
        with open(self.log_path, "rb") as f:
            f.seek(idx * LOG_REC)
            data = f.read(LOG_REC)
        if len(data) < LOG_REC:
            return ""
        return _unpad(data)

    def _write_entry(self, text: str) -> int:
        line = text.strip().replace("\n", " ")
        if len(line.encode("utf-8")) > ENTRY_CHARS:
            line = line.encode("utf-8")[:ENTRY_CHARS].decode("utf-8", errors="ignore")
        with open(self.log_path, "ab") as f:
            f.write(_pad(line, LOG_REC))
        return self.count() - 1

    def tree_get(self, lo: int, hi: int) -> str | None:
        size = hi - lo
        path = self.tree_dir / str(size)
        if not path.exists():
            return None
        slot = lo // size
        with open(path, "rb") as f:
            f.seek(slot * TREE_REC)
            data = f.read(TREE_REC)
        if len(data) < TREE_REC:
            return None
        text = _unpad(data)
        return text if text else None

    def tree_set(self, lo: int, hi: int, text: str) -> None:
        size = hi - lo
        path = self.tree_dir / str(size)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(b"")
        slot = lo // size
        need = (slot + 1) * TREE_REC
        cur = path.stat().st_size
        if cur < need:
            with open(path, "ab") as f:
                f.write(b"\x00" * (need - cur))
        line = text.strip().replace("\n", " ")
        if len(line.encode("utf-8")) > ENTRY_CHARS:
            line = line.encode("utf-8")[:ENTRY_CHARS].decode("utf-8", errors="ignore")
        with open(path, "r+b") as f:
            f.seek(slot * TREE_REC)
            f.write(_pad(line, TREE_REC))

    def tree_forget(self, lo: int, hi: int) -> bool:
        size = hi - lo
        path = self.tree_dir / str(size)
        if not path.exists():
            return False
        slot = lo // size
        with open(path, "r+b") as f:
            f.seek(slot * TREE_REC)
            f.write(b"\x00" * TREE_REC)
        return True

    def note(self, text: str) -> dict[str, Any]:
        if not self.exists():
            self.init()
        idx = self._write_entry(text)
        pending = self._pending(limit=1)
        out: dict[str, Any] = {"index": idx, "text": text.strip()[:ENTRY_CHARS], "count": self.count()}
        if pending:
            lo, hi = pending[0]
            out["nap_needed"] = f"{lo}-{hi - 1}"
            out["nap_hint"] = (
                f"Compress memories #{lo}-{hi - 1} into one line (max {ENTRY_CHARS} bytes). "
                f"Keep lasting effect, invent nothing. Then call memory_nap with range and summary."
            )
        return out

    def _pending(self, limit: int = 8) -> list[tuple[int, int]]:
        T = self.count()
        if T < 2:
            return []
        todo: list[tuple[int, int]] = []
        size = 2
        while size <= T:
            for lo in range(0, T - size + 1, size):
                hi = lo + size
                if self.tree_get(lo, hi) is None:
                    todo.append((lo, hi))
                    if len(todo) >= limit:
                        return todo
            size *= 2
        return todo

    def nap(self, lo: int, hi: int, summary: str) -> dict[str, Any]:
        if hi <= lo:
            return {"error": "invalid range"}
        size = hi - lo
        if size < 2 or (size & (size - 1)) != 0:
            return {"error": "range must be power-of-two length"}
        if lo % size != 0:
            return {"error": "range must be aligned"}
        self.tree_set(lo, hi, summary)
        return {"ok": True, "range": f"{lo}-{hi - 1}", "summary": summary.strip()[:ENTRY_CHARS]}

    def wake(self, budget: int = WAKE_LINES) -> str:
        if not self.exists():
            return "No memory store. Call memory_init first, or memory_note will create one."
        T = self.count()
        if T == 0:
            return "Memory is empty. Record facts with memory_note."
        blocks = cover(T, budget)
        lines: list[str] = [f"## OptMem wake ({T} entries)"]
        for lo, hi in blocks:
            if hi - lo == 1:
                text = self._read_entry(lo)
                lines.append(f"#{lo} {text}")
            else:
                summary = self.tree_get(lo, hi)
                if summary:
                    lines.append(f"#{lo}-{hi - 1} {summary}")
                else:
                    chunk = [self._read_entry(i) for i in range(lo, min(hi, T))]
                    lines.append(f"#{lo}-{hi - 1} [raw] " + " | ".join(c for c in chunk if c)[:ENTRY_CHARS])
        pending = self._pending(limit=3)
        if pending:
            lines.append("")
            lines.append("Pending compressions: " + ", ".join(f"{a}-{b - 1}" for a, b in pending))
        return "\n".join(lines)

    def recall(self, pattern: str, limit: int = 30) -> str:
        if not self.exists() or self.count() == 0:
            return "No memories."
        try:
            rx = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return f"Invalid regex: {e}"
        hits: list[str] = []
        T = self.count()
        for i in range(T):
            text = self._read_entry(i)
            if rx.search(text):
                hits.append(f"#{i} {text}")
                if len(hits) >= limit:
                    break
        if not hits:
            return f"No matches for /{pattern}/"
        return f"Recall /{pattern}/ ({len(hits)} hits):\n" + "\n".join(hits)

    def zoom(self, lo: int, hi: int) -> str:
        if hi <= lo:
            return "Invalid range"
        T = self.count()
        hi = min(hi, T)
        size = hi - lo
        if size == 1:
            return f"#{lo} {self._read_entry(lo)}"
        mid = (lo + hi) // 2
        left = self.tree_get(lo, mid) if mid - lo > 1 else self._read_entry(lo)
        right = self.tree_get(mid, hi) if hi - mid > 1 else (self._read_entry(mid) if mid < T else "")
        lines = [f"Zoom #{lo}-{hi - 1}:"]
        if mid - lo == 1:
            lines.append(f"  #{lo} {left}")
        else:
            lines.append(f"  #{lo}-{mid - 1} {left or '[no summary]'}")
        if hi - mid == 1:
            lines.append(f"  #{mid} {right}")
        else:
            lines.append(f"  #{mid}-{hi - 1} {right or '[no summary]'}")
        return "\n".join(lines)

    def forget(self, lo: int, hi: int) -> str:
        if self.tree_forget(lo, hi):
            return f"Forgot summary #{lo}-{hi - 1}. Next nap can rebuild it."
        return f"No summary at #{lo}-{hi - 1}."
