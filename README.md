# Production-Grade Multi-Modal RAG

An ultra-low latency, production-ready Research-Augmented Generation (RAG) system with support for Text, Audio, Video, and Image indexing. Designed for multi-tenancy and high compliance (SOC2/GDPR).

## 🚀 Key Features
- **Conversational RAG**: Chat history persistence with dialogue context awareness.
- **Async Ingestion**: High-throughput pipeline for Text, Audio, Image, and Video.
- **Cloud Native**: Integrated AWS S3 storage with CloudFront URL distribution.
- **Hotswappable**: Switch LLMs (GPT-4, Claude) and Embedders instantly via config.
- **Production Gateway**: Traefik with SSL (80/443), Rate Limiting, and ForwardAuth.
- **Admin Module**: Secure tenant onboarding and lifecycle management using Basic Auth.

## 🛠 Tech Stack
- **API**: FastAPI, Traefik
- **Storage**: Qdrant (Vector), PostgreSQL (Meta), Redis (Cache), AWS S3 (Blobs)
- **CDN**: AWS CloudFront
- **Workers**: Celery, Redis
- **Models**: Whisper, CLIP, BGE-Reranker, GPT-4/Claude/Llama

## 🏃 Getting Started
### Prerequisites
- Docker & Docker Compose
- API Keys (OpenAI/Anthropic) and AWS Credentials (if using S3)

### Running Locally
```bash
docker-compose up --build -d
```
Access the API at `http://localhost/api/v1/docs`. Refer to [USAGE_GUIDE.md](./USAGE_GUIDE.md) for onboarding instructions.

## 📅 Timeline
- [x] **Phase 1: Foundation**: Architecture design and documentation.
- [x] **Phase 2: Core API**: FastAPI setup, Auth, and Multi-tenancy logic.
- [x] **Phase 3: Ingestion**: Async workers for Text/Audio/Image/Video.
- [x] **Phase 4: Retrieval**: Vector store integration, Reranking, and Semantic Cache.
- [x] **Phase 5: Compliance**: PII scrubbing, audit logging, and SOC2 workflows.
- [x] **Phase 6: Infrastructure**: Multi-stage Docker optimization and Traefik SSL.
- [x] **Phase 7: Cloud & Chat**: AWS S3/CloudFront integration and Chat History.
- [x] **Phase 8: Administration**: Admin onboarding module and final user guide.
