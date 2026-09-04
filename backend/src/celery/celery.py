from src.core.config import settings

from celery import Celery

celery_app = Celery(
    'file_tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['src.celery.tasks'],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    worker_max_tasks_per_child=500,
    task_default_retry_delay=30,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_default_max_retries=3,
)
