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

The system uses a **Mandatory Multi-tenancy** model secured via **JWT Bearer Tokens**.

### How to get a Bearer Token
To interact with the API, you must first generate a token for your tenant.

**Endpoint**: `POST /api/v1/auth/token`  
**Example (cURL)**:
```bash
curl -X POST "http://localhost/api/v1/auth/token" \
     -H "Content-Type: application/json" \
     -d '{"tenant_id": "tenant-1", "client_secret": "your-secret-key"}'
```
*Note: The `client_secret` corresponds to the `SECRET_KEY` defined in your `.env` file.*

### Using the Token
Include the token in all subsequent requests:
- `X-Tenant-ID`: The unique identifier for your tenant (must match the token's subject).
- `Authorization`: `Bearer <your_token>`

---

## 3. Administration & Onboarding

Before a tenant can use the system, they must be onboarded by an administrator.

### Admin Authentication
The admin endpoints are secured via **HTTP Basic Auth** using predefined credentials in the `.env` file:
- `ADMIN_USERNAME`: Default is `admin`
- `ADMIN_PASSWORD`: Default is `supersecretadminpassword`

### Onboarding a Tenant
**Endpoint**: `POST /api/v1/admin/tenants`  
**Example (cURL)**:
```bash
curl -X POST "http://localhost/api/v1/admin/tenants" \
     -u "admin:supersecretadminpassword" \
     -H "Content-Type: application/json" \
     -d '{"id": "tenant-1", "name": "Acme Corp"}'
```

---

## 4. Core Workflows

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

## 6. High-Scale Operations

The system is optimized to handle 1M+ queries and 1M+ ingestions per day.

### Horizontal Scaling
- **API Nodes**: Scale the `api` service to handle multiple parallel requests. Traefik automatically load balances across instances.
- **Worker Replicas**: The `worker` service is configured with 4 default replicas in `docker-compose.yml`, each with a concurrency of 16 (64 parallel tasks). Scale this based on your ingestion queue depth.

### Connection Pooling
- **Database**: Optimized SQLAlchemy pool size (50) and max overflow (100) allow for handling massive concurrent DB sessions without overhead.
- **Redis**: High-capacity broker pool limits ensure worker-to-queue communication remains stable under load.

---

## 8. RAG Evaluation System

The system provides an automated way to measure the quality of the RAG pipeline.

### Step 1: Enable Shadow Tracking
Enable evaluation logging for a tenant via Redis:
```bash
redis-cli SET eval:tenant-1 true
```
Every query will now log a (Context, Query, Answer) triplet to the `audit_logs` table.

### Step 2: Trigger Evaluation Run
Run a background job to score the collected samples using G-Eval:
**Endpoint**: `POST /api/v1/eval/run`  
**Example (cURL)**:
```bash
curl -X POST "http://localhost/api/v1/eval/run" \
     -H "X-Tenant-ID: tenant-1" \
     -H "Authorization: Bearer my-admin-token"
```

### Step 3: View Quality Report
**Endpoint**: `GET /api/v1/eval/reports`  
The report provides:
- **Faithfulness**: How much the answer is grounded in context.
- **Answer Relevance**: How well the answer matches the query.
- **Context Precision**: Signal-to-noise ratio in retrieval.
- **Critique**: Feedback for samples with low scores.

---

## 9. API Testing (Postman)

A pre-configured Postman collection is available at `rag_api_postman_collection.json`.

### How to use:
1. **Import**: Open Postman and import the JSON file.
2. **Variables**: Update the **Collection Variables** (Base URL, Tokens, Admin Credentials) to match your environment.
3. **Run**: Use the organized folders (Administration, Ingestion, Chat, etc.) to test the full system lifecycle.

---

## 10. Troubleshooting

- **Check Logs**:
  ```bash
  docker-compose logs -f api      # API logs
  docker-compose logs -f worker   # Background processing logs
  ```
- **Gateway Status**: Visit `http://localhost:8080` to see the Traefik dashboard and verify routing/middlewares.
- **Storage**: If using `local` storage, files are stored in the `storage/` directory, organized by `tenant_id`.
