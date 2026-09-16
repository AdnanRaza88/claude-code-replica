from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .base import Tool, ToolResult


SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".agentforge",
}


class CodeGraphInput(BaseModel):
    action: str = Field(
        default="query",
        description="index | query | symbol | outline | callers | how_works",
    )
    query: str = ""
    path: str = "."
    max_results: int = 24


class CodeGraphTool(Tool):
    name = "code_graph"
    description = (
        "Structural code intelligence: index the workspace into a symbol graph "
        "and answer how-does-X-work / callers / outline queries without dumping files."
    )
    risk = "low"
    input_schema = CodeGraphInput

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.cwd()
        self.cache_path = self.root / ".agentforge" / "code_graph.json"
        self._graph: dict[str, Any] | None = None

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = CodeGraphInput(**input_data)
            action = (data.action or "query").lower().strip()
            if action == "index":
                graph = self._index(data.path)
                self._save(graph)
                self._graph = graph
                return ToolResult(
                    success=True,
                    output=(
                        f"indexed {graph['stats']['files']} files, "
                        f"{graph['stats']['symbols']} symbols, "
                        f"{graph['stats']['edges']} edges"
                    ),
                    data=graph["stats"],
                )

            graph = self._load()
            if graph is None:
                graph = self._index(data.path)
                self._save(graph)
                self._graph = graph

            q = (data.query or "").strip()
            if action == "outline":
                return self._outline(graph, q or data.path)
            if action == "symbol":
                return self._find_symbol(graph, q, data.max_results)
            if action == "callers":
                return self._callers(graph, q, data.max_results)
            if action == "how_works":
                return self._how_works(graph, q, data.max_results)
            return self._query(graph, q, data.max_results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _index(self, rel: str) -> dict[str, Any]:
        base = (self.root / rel).resolve()
        root = self.root.resolve()
        if not str(base).startswith(str(root)):
            raise ValueError("path outside workspace")

        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, str]] = []

        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                if not name.endswith(".py"):
                    continue
                fp = Path(dirpath) / name
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                    tree = ast.parse(text)
                except Exception:
                    continue
                rel_path = str(fp.relative_to(root)).replace("\\", "/")
                file_id = f"file:{rel_path}"
                nodes[file_id] = {
                    "id": file_id,
                    "kind": "file",
                    "name": name,
                    "path": rel_path,
                }
                self._walk_module(tree, rel_path, file_id, nodes, edges)

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "files": sum(1 for n in nodes.values() if n["kind"] == "file"),
                "symbols": sum(1 for n in nodes.values() if n["kind"] != "file"),
                "edges": len(edges),
            },
        }

    def _walk_module(
        self,
        tree: ast.AST,
        rel_path: str,
        file_id: str,
        nodes: dict[str, dict[str, Any]],
        edges: list[dict[str, str]],
    ) -> None:
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(
                        {
                            "src": file_id,
                            "dst": f"mod:{alias.name}",
                            "kind": "imports",
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                edges.append({"src": file_id, "dst": f"mod:{mod}", "kind": "imports"})
            elif isinstance(node, ast.ClassDef):
                sid = f"class:{rel_path}:{node.name}"
                nodes[sid] = {
                    "id": sid,
                    "kind": "class",
                    "name": node.name,
                    "path": rel_path,
                    "line": node.lineno,
                    "doc": ast.get_docstring(node) or "",
                }
                edges.append({"src": file_id, "dst": sid, "kind": "contains"})
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        mid = f"fn:{rel_path}:{node.name}.{item.name}"
                        nodes[mid] = {
                            "id": mid,
                            "kind": "method",
                            "name": f"{node.name}.{item.name}",
                            "path": rel_path,
                            "line": item.lineno,
                            "doc": ast.get_docstring(item) or "",
                        }
                        edges.append({"src": sid, "dst": mid, "kind": "contains"})
                        self._record_calls(item, mid, edges)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fid = f"fn:{rel_path}:{node.name}"
                nodes[fid] = {
                    "id": fid,
                    "kind": "function",
                    "name": node.name,
                    "path": rel_path,
                    "line": node.lineno,
                    "doc": ast.get_docstring(node) or "",
                }
                edges.append({"src": file_id, "dst": fid, "kind": "contains"})
                self._record_calls(node, fid, edges)

    def _record_calls(self, fn: ast.AST, src_id: str, edges: list[dict[str, str]]) -> None:
        for child in ast.walk(fn):
            if isinstance(child, ast.Call):
                name = self._call_name(child.func)
                if name:
                    edges.append({"src": src_id, "dst": f"call:{name}", "kind": "calls"})

    def _call_name(self, func: ast.AST) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            base = self._call_name(func.value)
            return f"{base}.{func.attr}" if base else func.attr
        return ""

    def _query(self, graph: dict[str, Any], q: str, limit: int) -> ToolResult:
        if not q:
            stats = graph.get("stats", {})
            return ToolResult(
                success=True,
                output=f"graph ready: {stats}",
                data=stats,
            )
        return self._how_works(graph, q, limit)

    def _find_symbol(self, graph: dict[str, Any], q: str, limit: int) -> ToolResult:
        if not q:
            return ToolResult(success=False, error="query required")
        needle = q.lower()
        hits = []
        for node in graph["nodes"].values():
            hay = f"{node.get('name','')} {node.get('path','')} {node.get('doc','')}".lower()
            if needle in hay:
                hits.append(node)
            if len(hits) >= limit:
                break
        lines = [
            f"{n['kind']} {n['name']}  {n.get('path','')}:{n.get('line','')}"
            for n in hits
        ]
        return ToolResult(
            success=True,
            output="\n".join(lines) if lines else "no symbols",
            data={"count": len(hits), "hits": hits},
        )

    def _outline(self, graph: dict[str, Any], path_or_name: str) -> ToolResult:
        needle = path_or_name.replace("\\", "/").lower()
        contained = []
        file_id = None
        for node in graph["nodes"].values():
            if node["kind"] == "file" and needle in node["path"].lower():
                file_id = node["id"]
                break
        if not file_id:
            return self._find_symbol(graph, path_or_name, 20)
        kids = [
            e["dst"]
            for e in graph["edges"]
            if e["src"] == file_id and e["kind"] == "contains"
        ]
        extra = []
        for e in graph["edges"]:
            if e["src"] in kids and e["kind"] == "contains":
                extra.append(e["dst"])
        ids = kids + extra
        lines = []
        for sid in ids:
            n = graph["nodes"].get(sid)
            if n:
                lines.append(f"{n['kind']} {n['name']} L{n.get('line','')}")
                contained.append(n)
        return ToolResult(
            success=True,
            output="\n".join(lines) if lines else "empty file",
            data={"file": file_id, "symbols": contained},
        )

    def _callers(self, graph: dict[str, Any], q: str, limit: int) -> ToolResult:
        if not q:
            return ToolResult(success=False, error="query required")
        needle = q.lower()
        hits = []
        for e in graph["edges"]:
            if e["kind"] != "calls":
                continue
            if needle not in e["dst"].lower() and needle not in e["src"].lower():
                continue
            src = graph["nodes"].get(e["src"], {"id": e["src"], "name": e["src"]})
            hits.append({"from": src.get("name"), "path": src.get("path"), "to": e["dst"]})
            if len(hits) >= limit:
                break
        lines = [f"{h['from']} ({h.get('path','')}) -> {h['to']}" for h in hits]
        return ToolResult(
            success=True,
            output="\n".join(lines) if lines else "no callers",
            data={"count": len(hits), "hits": hits},
        )

    def _how_works(self, graph: dict[str, Any], q: str, limit: int) -> ToolResult:
        if not q:
            return ToolResult(success=False, error="query required")
        needle = q.lower()
        matches = [
            n
            for n in graph["nodes"].values()
            if needle in n.get("name", "").lower()
            or needle in n.get("path", "").lower()
            or needle in n.get("doc", "").lower()
        ][:limit]
        if not matches:
            return ToolResult(success=True, output="no structural match", data={"hits": []})

        parts = ["Structural map:"]
        payload = []
        for n in matches:
            related = [
                e
                for e in graph["edges"]
                if e["src"] == n["id"] or e["dst"] == n["id"]
            ][:12]
            parts.append(
                f"- {n['kind']} {n['name']} @ {n.get('path','')}:{n.get('line','')}"
            )
            if n.get("doc"):
                parts.append(f"  {n['doc'][:180]}")
            for e in related:
                parts.append(f"  {e['kind']}: {e['src']} -> {e['dst']}")
            payload.append({"node": n, "edges": related})
        return ToolResult(success=True, output="\n".join(parts), data={"hits": payload})

    def _save(self, graph: dict[str, Any]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        slim = {
            "nodes": graph["nodes"],
            "edges": graph["edges"],
            "stats": graph["stats"],
        }
        self.cache_path.write_text(json.dumps(slim), encoding="utf-8")

    def _load(self) -> dict[str, Any] | None:
        if self._graph is not None:
            return self._graph
        if not self.cache_path.exists():
            return None
        try:
            self._graph = json.loads(self.cache_path.read_text(encoding="utf-8"))
            return self._graph
        except Exception:
            return None
