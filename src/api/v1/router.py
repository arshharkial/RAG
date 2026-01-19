from fastapi import APIRouter
from src.api.v1.endpoints import ingestion

api_v3_router = APIRouter()

api_v3_router.include_router(ingestion.router, prefix="/ingest", tags=["ingestion"])

@api_v3_router.get("/status")
async def get_status():
    return {"status": "ok", "message": "API V1 is running"}
