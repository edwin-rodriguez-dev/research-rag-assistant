from dataclasses import dataclass
from pathlib import Path
import psycopg
from pgvector.psycopg import register_vector
from research_rag.config import settings, required


@dataclass(frozen=True)
class DatabaseStatus:
    server_version: str
    has_vector: bool
    has_schema: bool
    document_count: int
    chunk_count: int
    acl_count: int
    audit_count: int


def connect(*, autocommit: bool = False):
    url = required(settings().database_url, "DATABASE_URL")
    conn = psycopg.connect(url, autocommit=autocommit)
    register_vector(conn)
    return conn


def init_schema(path: Path) -> None:
    url = required(settings().database_url, "DATABASE_URL")
    sql = path.read_text(encoding="utf-8")
    with psycopg.connect(url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def inspect_database(conn) -> DatabaseStatus:
    with conn.cursor() as cur:
        cur.execute("SHOW server_version;")
        server_version = str(cur.fetchone()[0])

        cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
        has_vector = cur.fetchone() is not None

        cur.execute(
            "SELECT 1 FROM information_schema.schemata WHERE schema_name = 'research_rag';"
        )
        has_schema = cur.fetchone() is not None

        if not has_schema:
            return DatabaseStatus(
                server_version=server_version,
                has_vector=has_vector,
                has_schema=False,
                document_count=0,
                chunk_count=0,
                acl_count=0,
                audit_count=0,
            )

        cur.execute("SELECT COUNT(*) FROM research_rag.documents;")
        doc_count = int(cur.fetchone()[0])

        cur.execute("SELECT COUNT(*) FROM research_rag.chunks;")
        chunk_count = int(cur.fetchone()[0])

        cur.execute("SELECT COUNT(*) FROM research_rag.document_acl;")
        acl_count = int(cur.fetchone()[0])

        cur.execute("SELECT COUNT(*) FROM research_rag.audit_log;")
        audit_count = int(cur.fetchone()[0])

        return DatabaseStatus(
            server_version=server_version,
            has_vector=has_vector,
            has_schema=True,
            document_count=doc_count,
            chunk_count=chunk_count,
            acl_count=acl_count,
            audit_count=audit_count,
        )
