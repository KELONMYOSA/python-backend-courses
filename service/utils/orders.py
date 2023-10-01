from datetime import datetime

from service.contracts import OrderForm, Order, OrderPosition
from service.utils.dao import get_menu_ids, get_menu_position_by_id, set_order, set_order_id_to_user


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
