import sys
import psycopg
from research_rag.config import settings, required
from research_rag.db import inspect_database


def verify_main() -> int:
    try:
        url = required(settings().database_url, "DATABASE_URL")
    except RuntimeError as err:
        print(f"Configuration error: {err}", file=sys.stderr)
        return 1

    try:
        with psycopg.connect(url) as conn:
            status = inspect_database(conn)
    except psycopg.Error as err:
        # Avoid printing connection string or credentials
        print(f"Database connection failed: {type(err).__name__}", file=sys.stderr)
        return 1

    print("PostgreSQL connection established successfully.")
    print(f"PostgreSQL server version: {status.server_version}")
    print(f"Vector extension exists: {'yes' if status.has_vector else 'no'}")
    print(f"Schema 'research_rag' exists: {'yes' if status.has_schema else 'no'}")
    print(f"Document count: {status.document_count}")
    print(f"Chunk count: {status.chunk_count}")
    print(f"ACL count: {status.acl_count}")
    print(f"Audit log count: {status.audit_count}")

    if not status.has_vector:
        print("Verification error: Required 'vector' extension is missing.", file=sys.stderr)
        return 1
    if not status.has_schema:
        print("Verification error: Required 'research_rag' schema is missing.", file=sys.stderr)
        return 1

    print("Database verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(verify_main())
