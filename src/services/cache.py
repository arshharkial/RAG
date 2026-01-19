import json
from typing import Optional, Dict, Any
import redis.asyncio as redis
from src.core.config import settings

class SemanticCache:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.ttl = 3600  # 1 hour

    async def get(self, tenant_id: str, query_vector_hash: str) -> Optional[Dict[str, Any]]:
        key = f"cache:{tenant_id}:{query_vector_hash}"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, tenant_id: str, query_vector_hash: str, response: Dict[str, Any]):
        key = f"cache:{tenant_id}:{query_vector_hash}"
        await self.redis.setex(
            key,
            self.ttl,
            json.dumps(response)
        )

semantic_cache = SemanticCache()
