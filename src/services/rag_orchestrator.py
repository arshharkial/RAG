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
        conversation_id: str,
        db,  # AsyncSession
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        import uuid
        from src.models.chat import Message, Conversation
        from sqlalchemy import select

        # 1. Fetch or initialize conversation context
        history_msgs = []
        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).limit(10)
        result = await db.execute(stmt)
        history_msgs = result.scalars().all()

        # 2. Save User Message
        user_msg_id = str(uuid.uuid4())
        user_msg = Message(
            id=user_msg_id,
            conversation_id=conversation_id,
            role="user",
            content=query_text
        )
        db.add(user_msg)
        await db.commit()

        # 3. Generate query embedding
        query_vector = await self.embedder.embed_text(query_text)
        query_hash = hashlib.sha256(query_text.encode()).hexdigest()
        
        # 4. Audit Log - Query Start
        from src.services.audit_logger import audit_logger
        await audit_logger.log(tenant_id, action="retrieval_query", payload={"query": query_text, "conversation_id": conversation_id})

        # 5. Check semantic cache
        cached_response = await semantic_cache.get(tenant_id, query_hash)
        if cached_response:
            yield {"type": "cache_hit", "content": cached_response}
            return

        # 6. Retrieve context
        hits = await vector_store.search(tenant_id, query_vector, limit=20)
        
        # 7. Rerank
        documents = [hit["payload"] for hit in hits]
        reranked_docs = await reranker.rerank(query_text, documents, top_k=5)
        
        # 8. Construct Context & Prompt
        context_str = self._format_context(reranked_docs)
        
        # Inject Chat History into Prompt
        history_str = "\n".join([f"{m.role}: {m.content}" for m in history_msgs])
        
        system_prompt = (
            "You are a helpful assistant. Use the provided context to answer the query. "
            "Use inline citations in the format [1], [2], etc. "
            "Maintain a conversational tone and acknowledge previous context if relevant."
        )
        
        prompt = f"Context Material:\n{context_str}\n\nRecent Chat History:\n{history_str}\n\nUser Query: {query_text}"
        
        # 9. Generate Response
        full_answer = ""
        async for chunk in self.llm.generate_stream(prompt, system_prompt=system_prompt):
            full_answer += chunk
            yield {"type": "content", "chunk": chunk}
            
        # 10. Save Assistant Message
        assistant_msg_id = str(uuid.uuid4())
        assistant_msg = Message(
            id=assistant_msg_id,
            conversation_id=conversation_id,
            role="assistant",
            content=full_answer,
            metadata_json={"references": self._get_references(reranked_docs)}
        )
        db.add(assistant_msg)
        await db.commit()

        # 11. Shadow Evaluation (Togglable)
        await self._handle_evaluation(tenant_id, query_text, reranked_docs, full_answer)

        # 12. Send References
        references = self._get_references(reranked_docs)
        yield {"type": "references", "content": references}
        
        source_material = self._get_source_material(reranked_docs)
        yield {"type": "source_material", "content": source_material}
        
        # 9. Cache the (non-streaming) result if needed
        # await semantic_cache.set(tenant_id, query_hash, {"answer": full_answer})

    async def _handle_evaluation(
        self, 
        tenant_id: str, 
        query: str, 
        contexts: List[Dict[str, Any]], 
        answer: str
    ):
        """
        Togglable evaluation pipeline.
        """
        from src.services.cache import semantic_cache
        # Check Redis for a feature flag: eval:tenant_id
        is_eval_on = await semantic_cache.redis.get(f"eval:{tenant_id}")
        
        if is_eval_on == "true":
            # 1. Shadow Log for Evaluation
            await audit_logger.log(
                tenant_id, 
                action="evaluation_shadow_log", 
                payload={
                    "query": query,
                    "answer": answer,
                    "contexts": [c.get("text") for c in contexts]
                }
            )
            # In production, this would trigger an async RAGAS/G-Eval job
            logger.info(f"Triggered background accuracy evaluation for tenant {tenant_id}")

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
