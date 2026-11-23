from pathlib import Path
from research_rag.db import init_schema

if __name__ == "__main__":
    init_schema(Path("sql/001_create_schema.sql"))
    print("research_rag schema initialized")
