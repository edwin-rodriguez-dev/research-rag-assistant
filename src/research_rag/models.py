from dataclasses import dataclass
from pathlib import Path
from datetime import date
from typing import Any

ROLES = ("PUBLIC", "RESEARCH", "PM", "ADMIN")

@dataclass
class SourceDocument:
    external_id: str
    title: str
    document_type: str
    source_type: str
    local_path: Path
    checksum: str
    classification: str = "PUBLIC"
    company: str | None = None
    source_url: str | None = None
    filing_date: date | None = None
    allowed_roles: list[str] | None = None
    metadata: dict[str, Any] | None = None

@dataclass
class Chunk:
    chunk_number: int
    text: str
    token_count: int

@dataclass
class SearchResult:
    chunk_id: int
    document_id: int
    title: str
    company: str | None
    document_type: str
    classification: str
    chunk_number: int
    text: str
    source_url: str | None
    score: float
    vector_rank: int | None = None
    keyword_rank: int | None = None
