import hashlib
from typing import List, Dict, Any, AsyncGenerator
from src.services.factory import LLMFactory, EmbedderFactory
from src.services.vector_store import vector_store
from src.services.reranker import reranker
from src.services.cache import semantic_cache

class RAGOrchestrator:
    def __init__(self):
        self.llm = LLMFactory.get_provider()
        self.embedder = EmbedderFactory.get_provider()

    async def query(
        self, 
        tenant_id: str, 
        query_text: str,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        # 1. Generate query embedding
        query_vector = await self.embedder.embed_text(query_text)
        query_hash = hashlib.sha256(query_text.encode()).hexdigest()
        
        # 2. Check semantic cache (simplified)
        cached_response = await semantic_cache.get(tenant_id, query_hash)
        if cached_response:
            yield {"type": "cache_hit", "content": cached_response}
            return

        # 3. Retrieve context from Vector DB
        hits = await vector_store.search(tenant_id, query_vector, limit=20)
        
        # 4. Rerank
        documents = [hit["payload"] for hit in hits]
        # In a real setup, we'd pass chunk text and query to reranker
        reranked_docs = await reranker.rerank(query_text, documents, top_k=5)
        
        # 5. Construct Context for LLM
        context_str = self._format_context(reranked_docs)
        
        # 6. Generate Response with Citations
        system_prompt = (
            "You are a helpful assistant. Use the provided context to answer the query. "
            "Use inline citations in the format [1], [2], etc. "
            "If the answer is not in the context, say you don't know."
        )
        
        prompt = f"Context:\n{context_str}\n\nQuery: {query_text}"
        
        # 7. Stream Response
        full_answer = ""
        async for chunk in self.llm.generate_stream(prompt, system_prompt=system_prompt):
            full_answer += chunk
            yield {"type": "content", "chunk": chunk}
            
        # 8. Send References and Source Material
        references = self._get_references(reranked_docs)
        yield {"type": "references", "content": references}
        
        source_material = self._get_source_material(reranked_docs)
        yield {"type": "source_material", "content": source_material}
        
        # 9. Cache the (non-streaming) result if needed
        # await semantic_cache.set(tenant_id, query_hash, {"answer": full_answer})

    def _format_context(self, docs: List[Dict[str, Any]]) -> str:
        context_parts = []
        for i, doc in enumerate(docs):
            context_parts.append(f"[{i+1}] {doc.get('text', '')}")
        return "\n\n".join(context_parts)

    def _get_references(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "index": i + 1,
                "text": doc.get("text", ""),
                "metadata": doc.get("metadata", {})
            } for i, doc in enumerate(docs)
        ]

    def _get_source_material(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Deduplicate source documents
        sources = {}
        for doc in docs:
            name = doc.get("metadata", {}).get("filename", "unknown")
            if name not in sources:
                sources[name] = {
                    "name": name,
                    "url": doc.get("metadata", {}).get("file_url", "#")
                }
        return list(sources.values())

rag_orchestrator = RAGOrchestrator()
