from celery import Celery
from .config import get_settings

settings = get_settings()
celery_app = Celery("hireiq", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

# Register tasks when the worker imports the Celery application.
from .tasks import interview_tasks  # noqa: E402,F401
