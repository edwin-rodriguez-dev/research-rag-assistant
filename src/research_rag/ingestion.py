import json
from openai import OpenAI

from research_rag.chunking import chunk_text
from research_rag.config import required, settings
from research_rag.db import connect
from research_rag.documents import discover_documents, load_document


class Embedder:
    def __init__(self):
        config = settings()
        self.client = OpenAI(
            api_key=required(config.openai_api_key, "OPENAI_API_KEY")
        )
        self.model = config.embedding_model
        self.dimensions = config.embedding_dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            dimensions=self.dimensions,
        )
        return [item.embedding for item in response.data]

    def one(self, text: str) -> list[float]:
        return self.embed([text])[0]


def ingest_all() -> None:
    paths = discover_documents()
    if not paths:
        raise RuntimeError(
            "No documents found; generate or fetch documents first."
        )

    embedder = Embedder()

    for path in paths:
        document, text = load_document(path)
        chunks = chunk_text(text)

        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO research_rag.documents (
                        external_id, title, company, document_type,
                        source_type, source_url, filing_date,
                        classification, local_path, checksum, metadata
                    )
                    VALUES (
                        %(external_id)s, %(title)s, %(company)s,
                        %(document_type)s, %(source_type)s,
                        %(source_url)s, %(filing_date)s,
                        %(classification)s, %(local_path)s,
                        %(checksum)s, %(metadata)s::jsonb
                    )
                    ON CONFLICT (external_id)
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        company = EXCLUDED.company,
                        document_type = EXCLUDED.document_type,
                        source_type = EXCLUDED.source_type,
                        source_url = EXCLUDED.source_url,
                        filing_date = EXCLUDED.filing_date,
                        classification = EXCLUDED.classification,
                        local_path = EXCLUDED.local_path,
                        checksum = EXCLUDED.checksum,
                        metadata = EXCLUDED.metadata
                    RETURNING id
                    """,
                    {
                        "external_id": document.external_id,
                        "title": document.title,
                        "company": document.company,
                        "document_type": document.document_type,
                        "source_type": document.source_type,
                        "source_url": document.source_url,
                        "filing_date": document.filing_date,
                        "classification": document.classification,
                        "local_path": str(document.local_path),
                        "checksum": document.checksum,
                        "metadata": json.dumps(document.metadata or {}),
                    },
                )
                document_id = cursor.fetchone()[0]

                cursor.execute(
                    "DELETE FROM research_rag.document_acl WHERE document_id = %s",
                    (document_id,),
                )
                for role in sorted(set(document.allowed_roles or ["PUBLIC"])):
                    cursor.execute(
                        """
                        INSERT INTO research_rag.document_acl (
                            document_id, allowed_role
                        )
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        (document_id, role),
                    )

                cursor.execute(
                    "DELETE FROM research_rag.chunks WHERE document_id = %s",
                    (document_id,),
                )
            connection.commit()

        total = 0
        for start in range(0, len(chunks), 32):
            batch = chunks[start:start + 32]
            vectors = embedder.embed([chunk.text for chunk in batch])

            with connect() as connection:
                with connection.cursor() as cursor:
                    for chunk, vector in zip(batch, vectors):
                        cursor.execute(
                            """
                            INSERT INTO research_rag.chunks (
                                document_id, chunk_number, text,
                                token_count, embedding
                            )
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                document_id,
                                chunk.chunk_number,
                                chunk.text,
                                chunk.token_count,
                                vector,
                            ),
                        )
                connection.commit()
                total += len(batch)

        print(f"Ingested {path.name}: {total} chunks")
