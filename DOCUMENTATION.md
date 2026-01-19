# Technical Documentation - Multi-Modal RAG

## 1. Overview
A production-grade RAG system for multi-modal context retrieval.

## 2. API Endpoints

### Ingestion
- `POST /api/v1/ingest/upload`: Upload media (Text, Audio, Image, Video).
  - **Headers**: `X-Tenant-ID` (Required), `Authorization` (Bearer token required)
  - **Form Data**: `file`, `media_type`

### Query
- `GET /api/v1/query/chat`: Stream a RAG response.
  - **Headers**: `X-Tenant-ID` (Required), `Authorization` (Bearer token required)
  - **Params**: `query`, `stream` (bool)
  - **Response**: NDJSON stream containing `content`, `references`, and `source_material`.

### Security (API Gateway)
- **ForwardAuth**: `GET /api/v1/auth/verify`. Traefik delegates auth to this endpoint.
- **SSL**: Traffic is accepted on port 80 (redirects to 443) and port 443 (HTTPS).
- **Rate Limiting**: Enforced at the gateway level (100 req/s average).

## 3. Internal Services

### RAG Orchestrator
Coordinates the following flow:
1. Hash query for **Semantic Cache**.
2. Log action to **Audit Logger**.
3. Generate **Embeddings** via factory.
4. Search **Vector Store** (Filtered by Tenant).
5. Pass hits to **Reranker**.
6. Stream through **LLM Provider**.
7. Run **Evaluation Toggle** (Redis-based shadow logging).

### Ingestion Worker
Handles:
1. File persistence to `storage/`.
2. **PII Scrubbing** on text data.
3. **Media extraction** (Whisper for audio, CLIP for images).
4. **Indexing** to Qdrant.

## 4. Configuration
Managed via `.env` and `src/core/config.py`.
- `LLM_PROVIDER`: `openai`, `anthropic`, or `mock`.
- `EMBEDDING_PROVIDER`: `openai` or `mock`.
- `REDIS_URL`: Connection string for cache and celery.

## 5. Feature Flags
- `eval:{tenant_id}`: Set to `true` in Redis to enable shadow accuracy evaluation logging.

## 6. Development
- **Local Setup**: `docker-compose up --build`
- **Tests**: `pytest tests/`
