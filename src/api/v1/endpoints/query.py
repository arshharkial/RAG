from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from src.services.rag_orchestrator import rag_orchestrator
import json

router = APIRouter()

@router.get("/chat")
async def chat(
    query: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    stream: bool = True
):
    """
    Query the RAG system and get a response with citations and source material.
    """
    async def response_generator():
        async for item in rag_orchestrator.query(x_tenant_id, query, stream=stream):
            yield json.dumps(item) + "\n"

    return StreamingResponse(response_generator(), media_type="application/x-ndjson")
