from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.core.database import get_db
from src.models.chat import Conversation, Message

router = APIRouter()

@router.get("/")
async def list_conversations(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
):
    """List all conversations for a tenant."""
    stmt = select(Conversation).where(Conversation.tenant_id == x_tenant_id).order_by(Conversation.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{conversation_id}/history")
async def get_chat_history(
    conversation_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all messages in a conversation."""
    # Ensure ownership
    stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.tenant_id == x_tenant_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and its messages."""
    stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.tenant_id == x_tenant_id)
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()
    
    if conv:
        await db.delete(conv)
        await db.commit()
    
    return {"status": "deleted"}
