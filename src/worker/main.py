from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "rag_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # High-throughput optimizations
    broker_pool_limit=100,           # Connection pooling for high concurrency
    task_acks_late=True,             # Acknowledge after execution for reliability
    worker_prefetch_multiplier=1,    # Avoid task hoarding, better for heterogeneous tasks
)

# Autodiscover tasks in src.worker.tasks
celery_app.autodiscover_tasks(["src.worker"])

@celery_app.task(name="run_evaluation_task")
def run_evaluation_task(tenant_id: str):
    """Async wrapper for the evaluation service."""
    import asyncio
    from src.services.evaluation import evaluation_service
    
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # This shouldn't happen in a fresh celery process but just in case
        return loop.create_task(evaluation_service.run_evaluation(tenant_id))
    else:
        return asyncio.run(evaluation_service.run_evaluation(tenant_id))
