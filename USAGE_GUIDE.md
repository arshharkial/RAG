# User Guide - Multi-Modal RAG System

This guide explains how to interact with the Multi-Modal RAG system, from initial setup to running advanced conversational queries.

---

## 1. Setup & Installation

### Prerequisites
- **Docker & Docker Compose**: Ensure you have the latest versions installed.
- **Environment Variables**: Copy `.env.example` to `.env` and fill in your keys:
  - `OPENAI_API_KEY`: Required for OpenAI LLM/Embeddings.
  - `ANTHROPIC_API_KEY`: Required if using Claude.
  - `AWS_ACCESS_KEY_ID` / `S3_BUCKET_NAME`: Required if `STORAGE_TYPE=s3`.

### Start the System
Run the following command in the project root:
```bash
docker-compose up --build -d
```
The API Gateway (Traefik) will be accessible at `http://localhost`.

---

## 2. Authentication & Multi-tenancy

The system uses a **Mandatory Multi-tenancy** model. Every request to the API must include the following headers:

- `X-Tenant-ID`: A unique identifier for your organization/tenant (e.g., `tenant-123`).
- `Authorization`: A Bearer token (e.g., `Bearer your-token`). 
  > [!NOTE]
  > In the current implementation, the Gateway delegates validation to the `/api/v1/auth/verify` endpoint. Ensure these headers are present to pass the ForwardAuth check.

---

## 3. Core Workflows

### A. Ingesting Data
You can upload Text, Audio, Image, or Video files. The system processes these asynchronously.

**Endpoint**: `POST /api/v1/ingest/upload`  
**Example (cURL)**:
```bash
curl -X POST "http://localhost/api/v1/ingest/upload" \
     -H "X-Tenant-ID: my-tenant" \
     -H "Authorization: Bearer my-secret" \
     -F "file=@/path/to/my_document.pdf" \
     -F "media_type=text"
```
Valid `media_type` values: `text`, `audio`, `image`, `video`.

### B. Starting a Chat
The RAG system maintains conversation context. To start a chat, you need a `conversation_id`.

**Endpoint**: `GET /api/v1/query/chat`  
**Example (cURL)**:
```bash
curl "http://localhost/api/v1/query/chat?query=What+is+in+the+document?&conversation_id=conv-001&stream=true" \
     -H "X-Tenant-ID: my-tenant" \
     -H "Authorization: Bearer my-secret"
```
The response is an **NDJSON stream** containing:
- `content`: The text chunk from the assistant.
- `references`: Citations and source metadata used to generate the answer.
- `type`: `cache_hit` if the answer was retrieved from the semantic cache.

### C. Managing Conversations
You can list, view, and delete chat history.

- **List Chats**: `GET /api/v1/conversations/`
- **View History**: `GET /api/v1/conversations/{id}/history`
- **Delete Chat**: `DELETE /api/v1/conversations/{id}`

---

## 4. Advanced Features

### Semantic Cache
The system caches similar queries in Redis. If a new query is semantically identical (>0.98 similarity) to a previous one, the response is delivered instantly from cache, bypassing the LLM and saving costs.

### Accuracy Evaluation (Shadow Mode)
You can toggle shadow evaluation for specific tenants by setting a flag in Redis:
```bash
redis-cli SET eval:my-tenant true
```
When enabled, the system logs the (Query, Context, Answer) triplet to an evaluation table for offline analysis with `RAGAS` or `G-Eval`.

---

## 5. Troubleshooting

- **Check Logs**:
  ```bash
  docker-compose logs -f api      # API logs
  docker-compose logs -f worker   # Background processing logs
  ```
- **Gateway Status**: Visit `http://localhost:8080` to see the Traefik dashboard and verify routing/middlewares.
- **Storage**: If using `local` storage, files are stored in the `storage/` directory, organized by `tenant_id`.
