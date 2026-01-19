from typing import List, AsyncGenerator, Optional
from src.services.base import BaseLLM, BaseEmbedder
from src.services.factory import LLMFactory, EmbedderFactory

class MockLLM(BaseLLM):
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return f"Mock response to: {prompt[:50]}..."

    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        response = f"Mock streaming response to: {prompt[:50]}..."
        for word in response.split():
            yield word + " "

class MockEmbedder(BaseEmbedder):
    async def embed_text(self, text: str) -> List[float]:
        return [0.1] * 1536  # Default size for many models

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 1536 for _ in texts]

    async def embed_image(self, image_path: str) -> List[float]:
        return [0.2] * 512

# Register providers
LLMFactory.register("mock", MockLLM)
EmbedderFactory.register("mock", MockEmbedder)
