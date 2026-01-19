from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from src.services.rag_orchestrator import rag_orchestrator
import json

router = APIRouter()

@router.get("/chat")
async def chat(
    query: str,
    conversation_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db),
    stream: bool = True
):
    """
    Query the RAG system and get a response with context from the chat history.
    """
    import uuid
    from src.models.chat import Conversation
    from sqlalchemy import select

    # Ensure conversation exists
    stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.tenant_id == x_tenant_id)
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()
    
    if not conv:
        conv = Conversation(id=conversation_id, tenant_id=x_tenant_id, title=f"Chat {query[:20]}...")
        db.add(conv)
        await db.commit()

    async def response_generator():
        async for item in rag_orchestrator.query(x_tenant_id, query, conversation_id, db, stream=stream):
            yield json.dumps(item) + "\n"

    return StreamingResponse(response_generator(), media_type="application/x-ndjson")
