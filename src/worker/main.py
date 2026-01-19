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
)

# Autodiscover tasks in src.worker.tasks
celery_app.autodiscover_tasks(["src.worker"])

@celery_app.task(name="health_check_task")
def health_check_task():
    return {"status": "ok", "message": "Celery worker is healthy"}
