import os
import time

from celery import Celery

RMQ_URL = os.getenv("RMQ_URL")
REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery('tasks', broker=RMQ_URL, backend=REDIS_URL)


# Логика для обработки заказа
@celery_app.task(name="order.process")
def process_order(order_items: list[dict]) -> str:
    total_price = sum(item["price"] for item in order_items)
    time.sleep(5)

    return f"Заказ успешно обработан. Общая сумма: {total_price}"
