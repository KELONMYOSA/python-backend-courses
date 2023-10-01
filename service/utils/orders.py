from datetime import datetime

from service.contracts import OrderForm, Order, OrderPosition
from service.utils.dao import get_menu_ids, get_menu_position_by_id, set_order, set_order_id_to_user, \
    get_order_ids_by_email, get_order_by_id


# Проверяем наличие позиций в заказе
def check_order_form(order_form: list[OrderForm]) -> bool:
    if not order_form:
        return False

    menu_ids = get_menu_ids()
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
    for pos in order_form:
        menu_position = get_menu_position_by_id(pos.menu_position_id)
        count = pos.count
        order_positions.append(OrderPosition(count=count, menu_position=menu_position))
        total_price += count * menu_position.price

    order = Order(time=datetime.utcnow(), total_price=total_price, positions=order_positions)

    # Записываем заказ в БД и присваиваем id заказу
    order_id = set_order(order)
    order.id = order_id

    # Присваиваем заказ пользователю
    set_order_id_to_user(email, order_id)

    return order


# Получение заказов пользователя
def get_orders_by_email(email: str) -> list[Order]:
    # Получаем список id заказов
    ids = get_order_ids_by_email(email)
    if ids is None:
        return []

    # Получаем заказы по id
    orders = []
    for order_id in ids:
        order = get_order_by_id(order_id)
        if order is not None:
            orders.append(order)

    return orders


# Получение заказов пользователя
def get_order_by_id_and_email(email: str, order_id: int) -> Order | None:
    # Получение id заказов и проверка принадлежности пользователю
    ids = get_order_ids_by_email(email)
    if ids is None:
        return None
    if order_id not in ids:
        return None

    # Получаем заказ по id
    order = get_order_by_id(order_id)

    return order
