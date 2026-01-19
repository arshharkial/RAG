import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from src.core.database import get_db
from src.core.config import settings
from src.models.ingestion import Tenant

router = APIRouter()
security = HTTPBasic()

# Schemas
class TenantCreate(BaseModel):
    id: str
    name: str

class TenantRead(BaseModel):
    id: str
    name: str
    created_at: str

def get_admin_user(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = settings.ADMIN_USERNAME.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = settings.ADMIN_PASSWORD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.post("/tenants", response_model=TenantCreate, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    admin_user: str = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Onboard a new tenant into the system."""
    # Check if exists
    stmt = select(Tenant).where(Tenant.id == tenant_data.id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tenant ID already exists")

    tenant = Tenant(id=tenant_data.id, name=tenant_data.name)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant

@router.get("/tenants")
async def list_tenants(
    admin_user: str = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all tenants onboarded in the system."""
    stmt = select(Tenant).order_by(Tenant.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    admin_user: str = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Offboard a tenant and delete all associated data (Metadata)."""
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    await db.delete(tenant)
    await db.commit()
    return {"status": "deleted", "tenant_id": tenant_id}
