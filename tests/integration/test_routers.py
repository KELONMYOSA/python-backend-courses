import json

import pytest

from main import app

from fastapi.testclient import TestClient

from service.contracts import OrderForm, OrderEncoder


class TestRegister:
    # Тест на успешную регистрацию
    def test_register_correct_credentials(self):
        with TestClient(app) as client:
            response = client.post("/register", json={"email": "nonexisting_email@example.com", "password": "password"})
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert response.json()["token_type"] == "bearer"

    # Тест на валидность электронной почты
    def test_register_invalid_email(self):
        with TestClient(app) as client:
            response = client.post("/register", json={"email": "invalid_email", "password": "password"})
            assert response.status_code == 403
            assert response.json() == {'detail': 'Email validation error'}

    # Тест на существование пользователя с указанной электронной почтой
    def test_register_existing_email(self):
        with TestClient(app) as client:
            response = client.post("/register", json={"email": "test@mail.ru", "password": "password"})
            assert response.status_code == 403
            assert response.json() == {'detail': 'A user with this email already exists'}

    #  Тест на пустой пароль
    def test_register_empty_password(self):
        with TestClient(app) as client:
            response = client.post("/register", json={"email": "example@example.com", "password": ""})
            assert response.status_code == 403
            assert response.json() == {'detail': 'The password cannot be empty'}


class TestLogin:
    # Тест на корректные учетные данные
    def test_login_correct_credentials(self):
        with TestClient(app) as client:
            response = client.post("/login", data={"username": "test@mail.ru", "password": "test"})
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert response.json()["token_type"] == "bearer"

    #  Тест на неправильное имя пользователя
    def test_login_incorrect_username(self):
        with TestClient(app) as client:
            response = client.post("/login", data={"username": "nonexisting_email@example.com", "password": "wrong"})
            assert response.status_code == 401
            assert response.json() == {'detail': 'Incorrect username or password'}

    # Тест на неправильный пароль
    def test_login_incorrect_password(self):
        with TestClient(app) as client:
            response = client.post("/login", data={"username": "test@mail.ru", "password": "wrong"})
            assert response.status_code == 401
            assert response.json() == {'detail': 'Incorrect username or password'}


class TestGetCurrentUser:
    # Тест на успешное получение данных аутентифицированного пользователя
    def test_get_current_user(self, auth_token):
        with TestClient(app) as client:
            response = client.get("/me", headers={"Authorization": f"Bearer {auth_token}"})
            assert response.status_code == 200
            user_data = json.loads(response.content)
            assert user_data["name"] == "admin"
            assert user_data["email"] == "admin@mail.ru"

    # Тест на получение данных без аутентификации
    def test_get_current_user_unauthenticated(self):
        with TestClient(app) as client:
            response = client.get("/me")
            assert response.status_code == 401
            assert json.loads(response.content)["detail"] == "Not authenticated"


class TestSetUserOrder:
    # Тест на корректную форму и аутентифицированного пользователя
    def test_set_order_correct_form(self, auth_token):
        with TestClient(app) as client:
            order_form = [OrderForm(menu_position_id=2, count=2), OrderForm(menu_position_id=5, count=3)]
            response = client.post("/order", headers={"Authorization": f"Bearer {auth_token}"},
                                   content=json.dumps(order_form, cls=OrderEncoder))
            assert response.status_code == 200
            order_data = json.loads(response.content)
            assert order_data["total_price"] == 880

    # Тест на корректную форму и не аутентифицированного пользователя
    def test_set_order_correct_form_unauthenticated(self):
        with TestClient(app) as client:
            order_form = [OrderForm(menu_position_id=2, count=2), OrderForm(menu_position_id=5, count=3)]
            response = client.post("/order", content=json.dumps(order_form, cls=OrderEncoder))
            assert response.status_code == 401
            assert json.loads(response.content)["detail"] == "Not authenticated"

    # order_form0 - Тест на пустую форму заказа
    # order_form1 - Тест на некорректное количество позиций в форме заказа
    # order_form2 - Тест на некорректный идентификатор позиции в форме заказа
    @pytest.mark.parametrize(
        "order_form",
        [
            ([]),
            ([OrderForm(menu_position_id=2, count=0)]),
            ([OrderForm(menu_position_id=99, count=3)]),
        ],
    )
    def test_set_order_invalid_form(self, auth_token, order_form):
        with TestClient(app) as client:
            response = client.post("/order", headers={"Authorization": f"Bearer {auth_token}"},
                                   content=json.dumps(order_form, cls=OrderEncoder))
            assert response.status_code == 404
            assert json.loads(response.content)["detail"] == "The items specified in the order were not found"


class TestGetUserOrders:
    # Тест для пользователя, у которого есть заказы
    def test_get_user_orders_with_orders(self, auth_token):
        with TestClient(app) as client:
            response = client.get("/orders", headers={"Authorization": f"Bearer {auth_token}"})
            assert response.status_code == 200
            orders_data = json.loads(response.content)
            assert orders_data[0]["id"] == 2
            assert orders_data[1]["id"] == 3

    # Тест для пользователя, у которого нет заказов
    def test_get_user_orders_no_orders(self, auth_token_no_orders):
        with TestClient(app) as client:
            response = client.get("/orders", headers={"Authorization": f"Bearer {auth_token_no_orders}"})
            assert response.status_code == 200
            assert response.content == b"[]"

    # Тест без аутентификации
    def test_get_user_orders_unauthenticated(self):
        with TestClient(app) as client:
            response = client.get("/orders")
            assert response.status_code == 401
            assert json.loads(response.content)["detail"] == "Not authenticated"


class TestGetUserOrderById:
    # Тест для аутентифицированного пользователя с корректным id
    def test_get_user_order_by_id(self, auth_token):
        with TestClient(app) as client:
            order_id = 2
            response = client.get(f"/order/{order_id}", headers={"Authorization": f"Bearer {auth_token}"})
            assert response.status_code == 200
            orders_data = json.loads(response.content)
            assert orders_data["id"] == 2

    # Тест для пользователя, у которого нет заказа с таким id
    def test_get_user_order_by_id_invalid_id(self, auth_token):
        with TestClient(app) as client:
            order_id = 99
            response = client.get(f"/order/{order_id}", headers={"Authorization": f"Bearer {auth_token}"})
            assert response.status_code == 404
            assert json.loads(response.content)["detail"] == "An order with this id was not found for this user"

    # Тест без аутентификации
    def test_get_user_order_by_id_unauthenticated(self):
        with TestClient(app) as client:
            response = client.get("/order/1")
            assert response.status_code == 401
            assert json.loads(response.content)["detail"] == "Not authenticated"
