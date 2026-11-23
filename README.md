# Research RAG Assistant

Small, enterprise-shaped RAG project demonstrating document processing, embeddings, pgvector, hybrid search, governance, citations, evals, and CI.

## Architecture

```text
SEC + synthetic docs -> parse/chunk -> embeddings -> PostgreSQL/pgvector
                                             |
question -> vector search + keyword search -> RRF -> top chunks -> LLM -> cited answer
                                             |
                                      ACL filter + audit
```

Version 1 intentionally has no Redis, Pinecone, OpenSearch, S3, Kubernetes, or agents.

## Setup

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
```

2. Copy `.env.example` to `.env` and set `DATABASE_URL`, `OPENAI_API_KEY`, and `SEC_USER_AGENT`.

3. Initialize PostgreSQL:

```powershell
.venv\Scripts\python.exe scripts/init_db.py
```

4. Generate synthetic governed documents:

```powershell
.venv\Scripts\python.exe scripts/generate_synthetic_docs.py
```

5. Fetch public SEC filings:

```powershell
.venv\Scripts\python.exe scripts/fetch_sec_documents.py
```

6. Parse, chunk, embed, and store documents:

```powershell
.venv\Scripts\python.exe scripts/ingest_documents.py
```

7. Inspect retrieval without generation:

```powershell
.venv\Scripts\python.exe scripts/search.py "What is Alpha Fund's main liquidity risk?" --role RESEARCH
```

8. Run the UI:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

9. Unit tests:

```powershell
.venv\Scripts\python.exe -m pytest
```

10. RAG evals (uses DB + OpenAI):

```powershell
.venv\Scripts\python.exe evals/run_evals.py
```

## Governance roles

- PUBLIC: public documents
- RESEARCH: public + research-authorized documents
- PM: public + PM-authorized documents
- ADMIN: all documents

Authorization is applied in the SQL retrieval query before chunks enter model context.
