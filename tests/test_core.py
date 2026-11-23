from research_rag.chunking import chunk_text
from research_rag.governance import may_access
from research_rag.models import SearchResult
from research_rag.retrieval import rrf


def search_result(identifier: int) -> SearchResult:
    return SearchResult(
        identifier,
        identifier,
        f"Doc {identifier}",
        None,
        "TEST",
        "PUBLIC",
        0,
        "text",
        None,
        0.0,
    )


def test_chunking():
    text = "\n\n".join(
        f"P{index} " + "word " * 100
        for index in range(10)
    )
    chunks = chunk_text(
        text,
        target_tokens=200,
        overlap_tokens=25,
    )
    assert len(chunks) > 1
    assert all(chunk.text and chunk.token_count > 0 for chunk in chunks)


def test_permissions():
    assert may_access("ADMIN", ["PM"])
    assert not may_access("RESEARCH", ["PM", "ADMIN"])
    assert may_access("PUBLIC", ["PUBLIC", "PM"])


def test_rrf_rewards_overlap():
    fused = rrf(
        [search_result(1), search_result(2)],
        [search_result(2), search_result(3)],
    )
    assert fused[0].chunk_id == 2
    assert fused[0].vector_rank == 2
    assert fused[0].keyword_rank == 1
