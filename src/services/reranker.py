from typing import List, Dict, Any
from abc import ABC, abstractmethod

class BaseReranker(ABC):
    @abstractmethod
    async def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        pass

class MockReranker(BaseReranker):
    async def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        # In a real implementation:
        # Use a Cross-Encoder (e.g., BGE-Reranker) to score pairs of (query, doc_text)
        # For mock, we just return the top_k as they are
        return documents[:top_k]

reranker = MockReranker()
