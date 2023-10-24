from celery import Celery
from celery.result import AsyncResult

from src.config import settings

celery_app = Celery('myapp', broker=settings.RMQ_URL, backend=settings.REDIS_URL)


# Получение результатов задач
def get_task_result(task_id):
    result = AsyncResult(task_id, app=celery_app)
    return result.result
