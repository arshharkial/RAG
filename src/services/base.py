from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Any, Optional

class BaseLLM(ABC):
    """Abstract base class for Large Language Model providers."""
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a complete response from the LLM."""
        pass

    @abstractmethod
    async def generate_stream(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM."""
        pass

class BaseEmbedder(ABC):
    """Abstract base class for text/multi-modal embedding providers."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a piece of text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of text."""
        pass

    @abstractmethod
    async def embed_image(self, image_path: str) -> List[float]:
        """Generate an embedding for an image."""
        pass
