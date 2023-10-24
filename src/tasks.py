import time

import src.celery_config as celery

celery_app = celery.celery_app


# Логика для обработки заказа
@celery_app.task
def process_order(order_id, order_items):
    total_price = sum(item['price'] for item in order_items)
    time.sleep(5)
    return f"Заказ {order_id} успешно обработан. Общая сумма: {total_price}"
