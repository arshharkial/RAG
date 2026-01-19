from fastapi import APIRouter
from src.api.v1.endpoints import ingestion, query, auth, conversations, admin

api_v3_router = APIRouter()

api_v3_router.include_router(ingestion.router, prefix="/ingest", tags=["ingestion"])
api_v3_router.include_router(query.router, prefix="/query", tags=["retrieval"])
api_v3_router.include_router(auth.router, prefix="/auth", tags=["security"])
api_v3_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_v3_router.include_router(admin.router, prefix="/admin", tags=["administration"])

@api_v3_router.get("/status")
async def get_status():
    return {"status": "ok", "message": "API V1 is running"}
