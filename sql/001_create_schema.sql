CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS research_rag;

CREATE TABLE IF NOT EXISTS research_rag.documents (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    company TEXT,
    document_type TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_url TEXT,
    filing_date DATE,
    classification TEXT NOT NULL DEFAULT 'PUBLIC',
    local_path TEXT NOT NULL,
    checksum TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS research_rag.document_acl (
    document_id BIGINT NOT NULL REFERENCES research_rag.documents(id) ON DELETE CASCADE,
    allowed_role TEXT NOT NULL,
    PRIMARY KEY (document_id, allowed_role)
);

CREATE TABLE IF NOT EXISTS research_rag.chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES research_rag.documents(id) ON DELETE CASCADE,
    chunk_number INTEGER NOT NULL,
    text TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    text_search TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', COALESCE(text, ''))
    ) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, chunk_number)
);

CREATE INDEX IF NOT EXISTS idx_chunks_text_search
    ON research_rag.chunks USING GIN(text_search);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
    ON research_rag.chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS research_rag.audit_log (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_name TEXT NOT NULL,
    user_role TEXT NOT NULL,
    question TEXT NOT NULL,
    retrieved_chunk_ids BIGINT[] NOT NULL DEFAULT '{}',
    retrieved_document_ids BIGINT[] NOT NULL DEFAULT '{}',
    answer_model TEXT,
    elapsed_ms INTEGER
);
