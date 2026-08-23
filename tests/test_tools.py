import asyncio
from pathlib import Path
import tempfile

from src.tools.file_tools import ReadTool, WriteTool, EditTool
from src.tools.search_tools import ProjectSearchTool


def test_write_read_edit():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write = WriteTool(root)
        read = ReadTool(root)
        edit = EditTool(root)

        async def run():
            r1 = await write.execute({"path": "a.txt", "content": "hello world"})
            assert r1.success
            r2 = await read.execute({"path": "a.txt"})
            assert r2.success
            assert "hello world" in r2.output
            r3 = await edit.execute(
                {"path": "a.txt", "old_string": "world", "new_string": "there"}
            )
            assert r3.success
            r4 = await read.execute({"path": "a.txt"})
            assert "hello there" in r4.output

        asyncio.run(run())


def test_search():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "x.py").write_text("def alpha():\n    return 1\n")
        search = ProjectSearchTool(root)

        async def run():
            r = await search.execute({"query": "alpha"})
            assert r.success
            assert "alpha" in r.output

        asyncio.run(run())
