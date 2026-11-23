from pathlib import Path
import psycopg
from pgvector.psycopg import register_vector
from research_rag.config import settings, required

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
