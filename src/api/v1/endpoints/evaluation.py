from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from src.core.database import get_db
from src.models.evaluation import EvaluationReport
from src.worker.main import run_evaluation_task

router = APIRouter()

@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_evaluation(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    admin_auth: str = Header(..., alias="Authorization") # Admin required
):
    """Trigger a background evaluation run for the tenant's RAG quality."""
    # Note: In a real system, we'd verify 'admin_auth' is really an admin
    job = run_evaluation_task.delay(x_tenant_id)
    return {"status": "queued", "job_id": job.id}

@router.get("/reports", response_model=List[Dict[str, Any]])
async def list_reports(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
):
    """List all evaluation reports for a tenant."""
    stmt = select(EvaluationReport).where(EvaluationReport.tenant_id == x_tenant_id).order_by(EvaluationReport.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific evaluation report (Summary & Metrics)."""
    stmt = select(EvaluationReport).where(EvaluationReport.id == report_id, EvaluationReport.tenant_id == x_tenant_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "id": report.id,
        "tenant_id": report.tenant_id,
        "metrics": {
            "faithfulness": report.avg_faithfulness,
            "relevance": report.avg_answer_relevance,
            "precision": report.avg_context_precision
        },
        "summary": report.summary_md,
        "created_at": report.created_at
    }
