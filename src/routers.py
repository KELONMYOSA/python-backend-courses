from fastapi import APIRouter

from src.celery_config import get_task_result
from src.contracts import OrderItem
from src.tasks import process_order

router = APIRouter()


# Создание нового заказа
@router.post("/create_order/")
async def create_order(order_items: list[OrderItem]):
    # Генерируем уникальный номер заказа
    order_id = len(order_items) + 1
    # Отправляем задачу на обработку
    process_order.delay(order_id, order_items)

    return {"message": "Заказ успешно создан", "order_id": order_id}


# Получение результата заказа
@router.get("/get_result/{task_id}")
async def get_result(task_id: str):
    result = get_task_result(task_id)

    if result is None:
        return {"status": "Задача в процессе выполнения"}
    return {"status": "Задача выполнена", "result": result}
