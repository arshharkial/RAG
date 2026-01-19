import pytest
from src.services.factory import LLMFactory, EmbedderFactory
from src.services.providers import MockLLM, MockEmbedder

def test_llm_factory_mock():
    # Make sure mock is registered
    LLMFactory.register("mock", MockLLM)
    provider = LLMFactory.get_provider("mock")
    assert isinstance(provider, MockLLM)

@pytest.mark.asyncio
async def test_mock_llm_generate():
    provider = MockLLM()
    response = await provider.generate("Hello world")
    assert "Mock response" in response

def test_embedder_factory_mock():
    EmbedderFactory.register("mock", MockEmbedder)
    provider = EmbedderFactory.get_provider("mock")
    assert isinstance(provider, MockEmbedder)

@pytest.mark.asyncio
async def test_mock_embedder_embed():
    provider = MockEmbedder()
    embedding = await provider.embed_text("sample")
    assert len(embedding) == 1536
    assert embedding[0] == 0.1
