import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    database_url: str
    openai_api_key: str
    sec_user_agent: str
    rag_model: str
    embedding_model: str
    embedding_dimensions: int
    top_k: int
    candidate_k: int

def settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        sec_user_agent=os.getenv("SEC_USER_AGENT", ""),
        rag_model=os.getenv("OPENAI_RAG_MODEL", "gpt-6-luna"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
        top_k=int(os.getenv("RAG_TOP_K", "6")),
        candidate_k=int(os.getenv("RAG_CANDIDATE_K", "20")),
    )

def required(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(
            f"{name} is not configured; copy .env.example to .env and set it."
        )
    return value
