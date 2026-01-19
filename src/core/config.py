from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "rag_db"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/rag_db"

    # Redis & Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Qdrant
    QDRANT_URL: str = "http://qdrant:6333"

    # API Keys
    OPENAI_API_KEY: str = "sk-..."
    ANTHROPIC_API_KEY: str = "sk-..."

    # Providers
    LLM_PROVIDER: str = "mock"
    EMBEDDING_PROVIDER: str = "mock"

    # AWS & S3 (Optional, defaults to local)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    CLOUDFRONT_DOMAIN: Optional[str] = None
    STORAGE_TYPE: str = "local"  # "local" or "s3"

    # Security
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
