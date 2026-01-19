# Technical Documentation - Multi-Modal RAG

Welcome to the internal documentation for the Multi-Modal RAG system.

## 1. Project Overview
This system is designed to provide ultra-low latency context retrieval for varied media types, supporting a multi-tenant production environment.

## 2. Architecture Deep-Dive

### Data Ingestion
All data enters via the `/ingest` endpoints. Depending on the `Content-Type`, the FastAPI gateway routes the file to a temporary S3/Minio bucket and triggers a Celery task.
- **Text**: Semantically chunked into 500-1000 tokens.
- **Audio**: Transcribed via Whisper, with overlapping window segments.
- **Image**: Embedded via CLIP ViT-L/14 for visual search.
- **Video**: Sampled at 1 frame every 2 seconds. Audio and visual vectors are merged or stored separately with temporal metadata.

### Retrieval Loop
1. **Query Input**: User sends a natural language query.
2. **Semantic Cache**: Redis is checked for high-similarity hits (>0.98 cosine similarity).
3. **Recall Stage**: Qdrant performs a search using HNSW, filtered by `tenant_id`.
4. **Precision Stage**: Top 100 results are re-ranked using a Cross-Encoder.
5. **Generation**: Top context is sent to the hotswapped LLM (GPT-4/Claude) for a streaming response.

## 3. Multi-tenancy
We use **logical isolation** via metadata filters.
- **Enforcement**: Middleware attaches `tenant_id` to the request context.
- **Safety**: The Vector DB query constructor *forces* a filter on `tenant_id`.

## 4. Compliance & Security
- **PII Scrubbing**: Applied at the ingestion worker level BEFORE data hits the vector store.
- **Encryption**: Secrets are managed via Vault/KMS; data volumes are encrypted at rest.

## 5. Developer Guide
- **Running tests**: `pytest` for unit/integration tests.
- **Adding a new LLM**: Inherit from `BaseLLM` and register in `LLMFactory`.
- **Infrastructure logs**: Viewable via Traefik Dashboard and Kibana.
