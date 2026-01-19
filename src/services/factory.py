from typing import Dict, Type
from src.services.base import BaseLLM, BaseEmbedder
from src.core.config import settings

class LLMFactory:
    _providers: Dict[str, Type[BaseLLM]] = {}

    @classmethod
    def register(cls, name: str, provider: Type[BaseLLM]):
        cls._providers[name] = provider

    @classmethod
    def get_provider(cls, name: Optional[str] = None) -> BaseLLM:
        name = name or settings.LLM_PROVIDER
        if name not in cls._providers:
            raise ValueError(f"LLM provider '{name}' not found.")
        return cls._providers[name]()

class EmbedderFactory:
    _providers: Dict[str, Type[BaseEmbedder]] = {}

    @classmethod
    def register(cls, name: str, provider: Type[BaseEmbedder]):
        cls._providers[name] = provider

    @classmethod
    def get_provider(cls, name: Optional[str] = None) -> BaseEmbedder:
        name = name or settings.EMBEDDING_PROVIDER
        if name not in cls._providers:
            raise ValueError(f"Embedding provider '{name}' not found.")
        return cls._providers[name]()
