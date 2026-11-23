from dataclasses import replace

from research_rag.config import settings
from research_rag.db import connect
from research_rag.ingestion import Embedder
from research_rag.models import SearchResult


def _from_row(
    row,
    score: float,
    *,
    vector_rank: int | None = None,
    keyword_rank: int | None = None,
) -> SearchResult:
    return SearchResult(
        chunk_id=row[0],
        document_id=row[1],
        title=row[2],
        company=row[3],
        document_type=row[4],
        classification=row[5],
        chunk_number=row[6],
        text=row[7],
        source_url=row[8],
        score=float(score),
        vector_rank=vector_rank,
        keyword_rank=keyword_rank,
    )


def vector_search(
    embedding: list[float],
    role: str,
    limit: int,
) -> list[SearchResult]:
    admin = role.upper() == "ADMIN"

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.id, d.id, d.title, d.company,
                    d.document_type, d.classification,
                    c.chunk_number, c.text, d.source_url,
                    1 - (c.embedding <=> %(embedding)s::vector) AS score
                FROM research_rag.chunks c
                JOIN research_rag.documents d
                    ON d.id = c.document_id
                WHERE (
                    %(admin)s
                    OR EXISTS (
                        SELECT 1
                        FROM research_rag.document_acl acl
                        WHERE acl.document_id = d.id
                          AND acl.allowed_role = %(role)s
                    )
                )
                ORDER BY c.embedding <=> %(embedding)s::vector
                LIMIT %(limit)s
                """,
                {
                    "embedding": embedding,
                    "admin": admin,
                    "role": role.upper(),
                    "limit": limit,
                },
            )
            rows = cursor.fetchall()

    return [
        _from_row(row, row[9], vector_rank=index + 1)
        for index, row in enumerate(rows)
    ]


def keyword_search(
    query: str,
    role: str,
    limit: int,
) -> list[SearchResult]:
    admin = role.upper() == "ADMIN"

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH q AS (
                    SELECT websearch_to_tsquery(
                        'english', %(query)s
                    ) AS query
                )
                SELECT
                    c.id, d.id, d.title, d.company,
                    d.document_type, d.classification,
                    c.chunk_number, c.text, d.source_url,
                    ts_rank_cd(c.text_search, q.query) AS score
                FROM research_rag.chunks c
                JOIN research_rag.documents d
                    ON d.id = c.document_id
                CROSS JOIN q
                WHERE c.text_search @@ q.query
                  AND (
                    %(admin)s
                    OR EXISTS (
                        SELECT 1
                        FROM research_rag.document_acl acl
                        WHERE acl.document_id = d.id
                          AND acl.allowed_role = %(role)s
                    )
                  )
                ORDER BY score DESC
                LIMIT %(limit)s
                """,
                {
                    "query": query,
                    "admin": admin,
                    "role": role.upper(),
                    "limit": limit,
                },
            )
            rows = cursor.fetchall()

    return [
        _from_row(row, row[9], keyword_rank=index + 1)
        for index, row in enumerate(rows)
    ]


def rrf(
    vector_results: list[SearchResult],
    keyword_results: list[SearchResult],
    k: int = 60,
) -> list[SearchResult]:
    by_id: dict[int, SearchResult] = {}
    scores: dict[int, float] = {}

    for rank, item in enumerate(vector_results, start=1):
        by_id[item.chunk_id] = replace(
            by_id.get(item.chunk_id, item),
            vector_rank=rank,
        )
        scores[item.chunk_id] = (
            scores.get(item.chunk_id, 0.0) + 1.0 / (k + rank)
        )

    for rank, item in enumerate(keyword_results, start=1):
        by_id[item.chunk_id] = replace(
            by_id.get(item.chunk_id, item),
            keyword_rank=rank,
        )
        scores[item.chunk_id] = (
            scores.get(item.chunk_id, 0.0) + 1.0 / (k + rank)
        )

    fused = [
        replace(item, score=scores[chunk_id])
        for chunk_id, item in by_id.items()
    ]
    return sorted(fused, key=lambda item: item.score, reverse=True)


class HybridRetriever:
    def __init__(self):
        self.config = settings()
        self.embedder = Embedder()

    def search(
        self,
        question: str,
        role: str,
        top_k: int | None = None,
    ) -> list[SearchResult]:
        embedding = self.embedder.one(question)
        candidate_k = self.config.candidate_k
        vector_results = vector_search(
            embedding,
            role,
            candidate_k,
        )
        keyword_results = keyword_search(
            question,
            role,
            candidate_k,
        )
        return rrf(vector_results, keyword_results)[
            :top_k or self.config.top_k
        ]
