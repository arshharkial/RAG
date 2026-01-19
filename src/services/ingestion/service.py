import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.ingestion import IngestionJob, JobStatus, MediaType
from src.services.storage import storage
from src.worker.main import celery_app

class IngestionService:
    @staticmethod
    async def create_job(
        db: AsyncSession,
        tenant_id: str,
        media_type: MediaType,
        file,
        filename: str
    ) -> IngestionJob:
        # 1. Upload file
        file_path = await storage.upload(file, tenant_id)
        
        # 2. Create job record
        job_id = str(uuid.uuid4())
        job = IngestionJob(
            id=job_id,
            tenant_id=tenant_id,
            media_type=media_type,
            file_path=file_path,
            filename=filename,
            status=JobStatus.PENDING
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # 3. Trigger Celery task
        celery_app.send_task(
            "process_ingestion_job",
            args=[job_id, tenant_id, media_type, file_path],
            queue="ingestion"
        )
        
        return job

ingestion_service = IngestionService()
