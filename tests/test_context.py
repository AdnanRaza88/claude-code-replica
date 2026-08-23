from src.services.context_service import ContextService, ContextIndexer


SAMPLE = """# System prompt
Base instructions.

## Harness
Harness rules here.

## Memory
Memory rules here.

## Agents
Agent rules.
"""


def test_indexer():
    idx = ContextIndexer()
    idx.index_text(SAMPLE)
    assert len(idx.headings) >= 3
    hits = idx.find_by_heading("Harness")
    assert hits
    body = idx.get_content(hits[0].context_id)
    assert "Harness rules" in body


def test_pack_builder():
    svc = ContextService()
    svc.indexer.index_text(SAMPLE)
    pack = svc.build_pack("harness", project_context="demo project")
    assert pack.domain == "harness"
    assert pack.token_estimate >= 0
    block = pack.to_prompt_block()
    assert "demo project" in block
