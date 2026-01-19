# Technical Documentation - Multi-Modal RAG

## 1. Overview
A production-grade RAG system for multi-modal context retrieval.

## 2. API Endpoints

### Ingestion
- `POST /api/v1/ingest/upload`: Upload media (Text, Audio, Image, Video).
  - **Headers**: `X-Tenant-ID` (Required), `Authorization` (Bearer token required)
  - **Form Data**: `file`, `media_type`

### Query
- `GET /api/v1/query/chat`: Stream a RAG response with conversational context.
  - **Headers**: `X-Tenant-ID` (Required), `Authorization` (Bearer token required)
  - **Params**: `query`, `conversation_id`, `stream` (bool)
  - **Response**: NDJSON stream containing `content`, `references`, and `source_material`.

### Conversations
- `GET /api/v1/conversations/`: List all conversations for the tenant.
- `GET /api/v1/conversations/{id}/history`: Get the full message history for a conversation.
- `DELETE /api/v1/conversations/{id}`: Delete a conversation and its messages.

### Administration
- `POST /api/v1/admin/tenants`: Onboard a new tenant.
- `GET /api/v1/admin/tenants`: List all onboarded tenants.
- `DELETE /api/v1/admin/tenants/{id}`: Offboard a tenant.
- **Auth**: HTTP Basic (Predefined admin credentials).

### Security (API Gateway)
- **ForwardAuth**: `GET /api/v1/auth/verify`. Traefik delegates auth to this endpoint.
- **SSL**: Traffic is accepted on port 80 (redirects to 443) and port 443 (HTTPS).
- **Rate Limiting**: Enforced at the gateway level (500 req/s average, 1000 burst).

## 3. Internal Services

### RAG Orchestrator
Coordinates the following flow:
1. Fetch 10 previous messages for **Context**.
2. Hash query for **Semantic Cache**.
3. Log action to **Audit Logger**.
4. Generate **Embeddings** via factory.
5. Search **Vector Store** (Filtered by Tenant).
6. Pass hits to **Reranker**.
7. Stream through **LLM Provider**.
8. Save assistant response to **PostgreSQL**.

### Ingestion Worker
Handles:
1. File persistence to **AWS S3** (or local `storage/`).
2. **CloudFront** URL generation for retrievals.
3. **PII Scrubbing** on text data.
4. **Media extraction** (Whisper for audio, CLIP for images, ffmpeg for video).
5. **Indexing** to Qdrant.

## 4. Configuration
Managed via `.env` and `src/core/config.py`.
- `STORAGE_TYPE`: `local` or `s3`.
- `ADMIN_USERNAME`/`ADMIN_PASSWORD`: Predefined admin credentials.
- `LLM_PROVIDER`: `openai`, `anthropic`, or `mock`.

## 5. Deployment
- **Local Setup**: `docker-compose up --build`
- **Kubernetes**: `helm install rag ./charts/rag-system`
- **Scaling**: HPAs enable horizontal pod autoscaling for API and Workers.
