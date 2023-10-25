from fastapi import APIRouter

from src.celery_config import celery_app, get_task_result
from src.contracts import OrderItems

router = APIRouter()


# Создание нового заказа
@router.post("/create_order/")
async def create_order(order_items: OrderItems):
    # Отправляем задачу на обработку
    task = celery_app.send_task("order.process", kwargs={"order_items": order_items.model_dump()})
    # Получаем уникальный номер задачи
    task_id = task.id

    return {"message": "Заказ успешно создан", "task_id": task_id}


# Получение результата заказа
@router.get("/get_result/{task_id}")
async def get_result(task_id: str):
    return get_task_result(task_id)
