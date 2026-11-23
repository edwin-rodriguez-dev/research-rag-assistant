from unittest.mock import MagicMock

from research_rag.chunking import chunk_text
from research_rag.db import DatabaseStatus, inspect_database
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


def test_inspect_database_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        ("16.2",),  # server_version
        (1,),       # has_vector
        (1,),       # has_schema
        (10,),      # document_count
        (50,),      # chunk_count
        (20,),      # acl_count
        (5,),       # audit_count
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    status = inspect_database(mock_conn)
    assert isinstance(status, DatabaseStatus)
    assert status.server_version == "16.2"
    assert status.has_vector is True
    assert status.has_schema is True
    assert status.document_count == 10
    assert status.chunk_count == 50
    assert status.acl_count == 20
    assert status.audit_count == 5


def test_inspect_database_missing_schema():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        ("16.2",),  # server_version
        (1,),       # has_vector
        None,       # has_schema is missing
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    status = inspect_database(mock_conn)
    assert status.has_vector is True
    assert status.has_schema is False
    assert status.document_count == 0
    assert status.chunk_count == 0
