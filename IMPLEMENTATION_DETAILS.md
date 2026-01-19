# Implementation Details - Multi-Modal RAG System

This document serves as the technical source of truth for the production-grade RAG system.

## 1. System Architecture
```mermaid
graph TD
    User((User/Client)) --> API[FastAPI Gateway]
    API --> Auth[Auth & Multi-tenancy Manager]
    Auth --> Orchestrator[RAG Orchestrator]
    
    API --> Ingestion[Async Ingestion Pipeline]
    Ingestion --> Queue[Redis Queue]
    Queue --> Worker[Celery Worker]
    
    Worker --> TextProc[Text Processor]
    Worker --> AudioProc[Audio Processor - Whisper]
    Worker --> ImageProc[Image Processor - CLIP/SigLIP]
    Worker --> VideoProc[Video Processor - Frame/Audio Extraction]
    
    TextProc & AudioProc & ImageProc & VideoProc --> Embedder[Abstract Embedding Interface]
    Embedder --> OpenAIEmbed[OpenAI]
    Embedder --> HuggingFaceEmbed[Local HuggingFace]
    
    Embedder --> VectorDB[(Vector Store - Qdrant/Milvus)]
    
    Orchestrator --> Retriever[Context Retriever]
    Retriever --> VectorDB
    
    Retriever --> LLM[Abstract LLM Interface]
    LLM --> GPT4[GPT-4o]
    LLM --> Claude[Claude 3.5]
    LLM --> LocalLLM[Llama 3]
    
    LLM --> Streamer[Streaming Response Handler]
    Streamer --> User
```

## 2. Technical Stack
- **Framework**: FastAPI (Async, Type-safe)
- **Metastore**: PostgreSQL (Multi-tenant, Audit logs)
- **Vector DB**: Qdrant (HNSW, Metadata filtering)
- **Cache**: Redis (Semantic cache, Session memory)
- **Task Queue**: Celery + RabbitMQ
- **API Gateway**: Traefik (Dynamic routing, Rate limiting)

## 3. Core Features
- **Multi-modal Ingestion**: Supports Text, Audio (Whisper), Image (CLIP), and Video (Frame extraction + ASR).
- **Hotswappable Providers**: Abstract interfaces for LLMs and Embedding models.
- **Ultra-Low Latency**: Semantic caching, connection pooling, and HNSW optimization.
- **Multi-tenancy**: Strict metadata-level isolation.
- **Advanced RAG**: Semantic Reranking (2-stage), Parent-Document Retrieval, and HyDE.
- **Togglable Evaluation**: Redis-managed accuracy evaluation (Shadow logging, RAGAS scoring).

## 4. Compliance (SOC2 & GDPR)
- **Encryption**: AES-256 (Rest), TLS 1.3 (Transit).
- **PII Scrubbing**: Integrated middleware via Presidio.
- **Right to be Forgotten**: Async data wiping jobs.
- **Audit Logs**: Immutable logs for all data access.

## 5. Deployment
- **Containerization**: Docker-first approach.
- **Orchestration**: Kubernetes (Helm charts) for production.
- **GPU support**: Pinned workers for model-intensive tasks.
