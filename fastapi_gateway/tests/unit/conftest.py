from datetime import datetime

import pytest

from service.contracts import MenuPosition, Order, OrderPosition
from service.utils.dao import Database


@pytest.fixture(autouse=True)
def mock_database(monkeypatch):
    def do_nothing(*args, **kwargs):
        pass

    def get_menu_ids(*args, **kwargs):
        return [1, 2, 3]

    def get_menu_position_by_id(*args, **kwargs):
        menu_id = args[1]
        menu = {
            1: MenuPosition(id=1, name="test1", price=100),
            2: MenuPosition(id=2, name="test2", price=200),
            3: MenuPosition(id=3, name="test3", price=300),
        }

        return menu[menu_id]

    def set_order(*args, **kwargs):
        return 1

    def get_order_ids_by_email(*args, **kwargs):
        email = args[1]
        if email == "existing_email@example.com":
            return [1, 2]
        else:
            return []

    def get_order_by_id(*args, **kwargs):
        order_id = args[1]
        orders = {
            1: Order(id=1, time=datetime.now(), total_price=100,
                     positions=[OrderPosition(count=1, menu_position=MenuPosition(id=1, name="test1", price=100))]),
            2: Order(id=2, time=datetime.now(), total_price=300,
                     positions=[OrderPosition(count=2, menu_position=MenuPosition(id=2, name="test2", price=150))]),
        }

        return orders[order_id]

    monkeypatch.setattr(Database, "__init__", do_nothing)
    monkeypatch.setattr(Database, "__exit__", do_nothing)
    monkeypatch.setattr(Database, "get_menu_ids", get_menu_ids)
    monkeypatch.setattr(Database, "get_menu_position_by_id", get_menu_position_by_id)
    monkeypatch.setattr(Database, "set_order", set_order)
    monkeypatch.setattr(Database, "set_order_id_to_user", do_nothing)
    monkeypatch.setattr(Database, "get_order_ids_by_email", get_order_ids_by_email)
    monkeypatch.setattr(Database, "get_order_by_id", get_order_by_id)
