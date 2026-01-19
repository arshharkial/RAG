from fastapi import APIRouter, Depends, UploadFile, File, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.models.ingestion import MediaType
from src.services.ingestion.service import ingestion_service

router = APIRouter()

@router.post("/upload")
async def upload_file(
    media_type: MediaType,
    file: UploadFile = File(...),
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file for ingestion. The file will be processed asynchronously based on its media type.
    """
    job = await ingestion_service.create_job(
        db=db,
        tenant_id=x_tenant_id,
        media_type=media_type,
        file=file,
        filename=file.filename
    )
    
    return {
        "job_id": job.id,
        "status": job.status,
        "media_type": job.media_type,
        "filename": job.filename
    }
