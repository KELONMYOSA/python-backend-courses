from datetime import datetime

from service.contracts import OrderForm, Order
from service.utils.orders import check_order_form, create_order, get_orders_by_email, get_order_by_id_and_email


class TestCheckOrderForm:
    # Тест на корректную форму заказа
    def test_check_order_form_correct_form(self):
        order_form = [OrderForm(count=1, menu_position_id=1)]
        assert check_order_form(order_form)

    # Тест на пустую форму заказа
    def test_check_order_form_empty_form(self):
        order_form = []
        assert not check_order_form(order_form)

    # Тест на некорректное количество позиций в форме заказа
    def test_check_order_form_invalid_count(self):
        order_form = [OrderForm(count=0, menu_position_id=1)]
        assert not check_order_form(order_form)

    # Тест на некорректный идентификатор позиции в форме заказа
    def test_check_order_form_invalid_menu_position_id(self):
        order_form = [OrderForm(count=1, menu_position_id=99)]
        assert not check_order_form(order_form)


class TestCreateOrder:
    # Тест корректного создания заказа
    def test_create_order(self):
        order_form = [OrderForm(menu_position_id=1, count=2), OrderForm(menu_position_id=2, count=3)]
        email = "existing_email@example.com"

        order = create_order(order_form, email)

        # Проверяем, что функция возвращает правильный тип данных
        assert isinstance(order, Order)

        # Проверяем, что order имеет правильные значения
        assert order.total_price == 800
        assert len(order.positions) == 2
        assert order.positions[0].count == 2
        assert order.positions[1].count == 3

        # Проверяем, что order.time - это текущая дата и время
        assert isinstance(order.time, datetime)
        assert order.time <= datetime.utcnow()

        # Проверяем order.id
        assert order.id == 1


class TestGetOrdersByEmail:
    # Тест, когда для заданного email нет заказов
    def test_get_orders_by_email_no_orders(self):
        email = "nonexisting_email@example.com"
        orders = get_orders_by_email(email)

        assert orders == []

    # Тест, когда для заданного email нет заказов
    def test_get_orders_by_email_with_orders(self):
        email = "existing_email@example.com"
        orders = get_orders_by_email(email)

        # Проверяем, что функция возвращает список
        assert isinstance(orders, list)

        # Проверяем, что возвращенный список содержит правильное количество заказов
        assert len(orders) == 2

        # Проверяем, что все заказы имеют правильные значения
        assert orders[0].id == 1
        assert orders[0].total_price == 100
        assert orders[1].id == 2
        assert orders[1].total_price == 300


class TestGetOrderByIdAndEmail:
    # Тест получения заказа для корректных данных
    def test_get_order_by_id_and_email_valid_order(self):
        email = "existing_email@example.com"
        order_id = 1
        order = get_order_by_id_and_email(email, order_id)

        # Проверяем, что функция возвращает объект класса Order
        assert isinstance(order, Order)

        # Проверяем, что возвращенный заказ имеет правильные значения
        assert order.id == 1
        assert order.total_price == 100

    # Тест для корректной почты и неправильного id
    def test_get_order_by_id_and_email_invalid_order(self):
        email = "existing_email@example.com"
        order_id = 99
        order = get_order_by_id_and_email(email, order_id)

        assert order is None

    # Тест, если для данной почты нет заказов
    def test_get_order_by_id_and_email_invalid_email(self):
        email = "nonexisting_email@example.com"
        order_id = 1
        order = get_order_by_id_and_email(email, order_id)

        assert order is None
