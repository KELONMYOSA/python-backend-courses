import json
from datetime import datetime

from aiohttp import ClientSession
from fastapi import HTTPException

from config import settings
from service.contracts import OrderForm, Order, OrderPosition, OrderEncoder
from service.utils.dao import Database


# Проверяем наличие позиций в заказе
def check_order_form(order_form: list[OrderForm]) -> bool:
    if not order_form:
        return False

    with Database() as db:
        menu_ids = db.get_menu_ids()

    for pos in order_form:
        if not pos.count > 0:
            return False
        if pos.menu_position_id not in menu_ids:
            return False

    return True


# Создание заказа
def create_order(order_form: list[OrderForm], email: str) -> Order:
    total_price = 0
    order_positions = []
    with Database() as db:
        for pos in order_form:
            menu_position = db.get_menu_position_by_id(pos.menu_position_id)
            count = pos.count
            order_positions.append(OrderPosition(count=count, menu_position=menu_position))
            total_price += count * menu_position.price

    order = Order(time=datetime.utcnow(), total_price=total_price, positions=order_positions)

    # Записываем заказ в БД и присваиваем id заказу
    with Database() as db:
        order_id = db.set_order(order)
    order.id = order_id

    # Присваиваем заказ пользователю
    with Database() as db:
        db.set_order_id_to_user(email, order_id)

    return order


# Получение заказов пользователя
def get_orders_by_email(email: str) -> list[Order]:
    # Получаем список id заказов
    with Database() as db:
        ids = db.get_order_ids_by_email(email)

    if ids is None:
        return []

    # Получаем заказы по id
    orders = []
    with Database() as db:
        for order_id in ids:
            order = db.get_order_by_id(order_id)
            if order is not None:
                orders.append(order)

    return orders


# Получение заказов пользователя
def get_order_by_id_and_email(email: str, order_id: int) -> Order | None:
    # Получение id заказов и проверка принадлежности пользователю
    with Database() as db:
        ids = db.get_order_ids_by_email(email)

    if ids is None:
        return None
    if order_id not in ids:
        return None

    # Получаем заказ по id
    with Database() as db:
        order = db.get_order_by_id(order_id)

    return order


# Получаем картинку с круговой диаграммой количества блюд в заказах
async def get_user_dishes_chart_png(email: str, orders: list[Order]):
    r_body = {
        "email": email,
        "orders": [order.positions for order in orders],
    }
    json_body = json.dumps(r_body, cls=OrderEncoder)

    async with ClientSession() as session:
        async with session.post(f"http://{settings.EXPRESS_CHARTS_SERVER}/chart/dishes", data=json_body,
                               headers={"Content-Type": "application/json"}) as resp:
            image_bytes = await resp.read()

    if resp.status == 200:
        return image_bytes
    else:
        raise HTTPException(status_code=resp.status)
