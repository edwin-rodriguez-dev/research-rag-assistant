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

## Cloud Deployment

To deploy the Research RAG Assistant to Streamlit Community Cloud with a managed cloud database:

1. Create a managed PostgreSQL database that supports pgvector (e.g., Neon, Supabase, AWS RDS, Tembo).
2. Obtain its PostgreSQL connection string (`postgresql://USER:PASSWORD@HOST:PORT/DATABASE`).
3. Temporarily set local `DATABASE_URL` in `.env` to that cloud connection string.
4. Run schema initialization:
   ```powershell
   .venv\Scripts\python.exe scripts/init_db.py
   ```
5. Run document generation and download (if not already fetched locally):
   ```powershell
   .venv\Scripts\python.exe scripts/generate_synthetic_docs.py
   .venv\Scripts\python.exe scripts/fetch_sec_documents.py
   ```
6. Ingest, embed, and store all documents and vectors into the cloud database:
   ```powershell
   .venv\Scripts\python.exe scripts/ingest_documents.py
   ```
7. Verify the cloud database schema and row counts:
   ```powershell
   .venv\Scripts\python.exe scripts/verify_database.py
   ```
8. Restore your local `.env` file's `DATABASE_URL` to point back to the local Docker database if desired.
9. Deploy `app.py` from your GitHub repository to Streamlit Community Cloud.
10. Add deployment secrets through the Streamlit Community Cloud app settings (see `.streamlit/secrets.toml.example`):
    - `DATABASE_URL`
    - `OPENAI_API_KEY`
    - `SEC_USER_AGENT`
    - `OPENAI_RAG_MODEL`
    - `OPENAI_EMBEDDING_MODEL`
    - `EMBEDDING_DIMENSIONS`
    - `RAG_TOP_K`
    - `RAG_CANDIDATE_K`
11. Open the deployed application URL and test retrieval, citation generation, and role-based ACL behavior.
