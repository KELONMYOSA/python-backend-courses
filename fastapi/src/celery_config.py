import json
import os

from celery import Celery

RMQ_URL = os.getenv("RMQ_URL")
REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery('tasks', broker=RMQ_URL, backend=REDIS_URL)


# Получение результатов задач
def get_task_result(task_id: str) -> dict:
    task = celery_app.AsyncResult(task_id)

    if task.state == 'SUCCESS':
        response = {
            'status': task.state,
            'result': task.get()
        }
    elif task.state == 'FAILURE':
        response = json.loads(task.backend.get(task.backend.get_key_for_task(task.id)).decode('utf-8'))
        del response['children']
        del response['traceback']
    else:
        response = {
            'status': task.state,
            'result': task.info
        }

    return response
