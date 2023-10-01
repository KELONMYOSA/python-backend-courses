import json
import sqlite3
from datetime import datetime

from service.contracts import UserReg, UserInDB, MenuPosition, Order, OrderEncoder, OrderPosition

DB_PATH = "database/database.sqlite"


# Получение всех email пользователей
def get_users_email() -> list[str]:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Выбираем всех пользователей
    cursor.execute('SELECT email FROM user')
    emails = cursor.fetchall()
    emails = list(map(lambda x: x[0], emails))

    # Закрываем соединение
    connection.close()

    return emails


# Создание нового пользователя
def set_user(user: UserReg, hashed_password: str):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Добавляем нового пользователя
    cursor.execute('INSERT INTO user (name, email, password) VALUES (?, ?, ?)',
                   (user.name, user.email, hashed_password))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


# Получаем данные пользователя по email
def get_user_by_email(email: str) -> UserInDB | None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Получаем данные пользователя
    cursor.execute('SELECT name, email, password FROM user WHERE email = ?', (email,))
    result = cursor.fetchall()
    user = None
    if result:
        user = UserInDB(name=result[0][0], email=result[0][1], hashed_password=result[0][2])

    # Закрываем соединение
    connection.close()

    return user


# Получение всех id позиций в меню
def get_menu_ids() -> list[int]:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Выбираем все позиции
    cursor.execute('SELECT id FROM menu')
    ids = cursor.fetchall()
    ids = list(map(lambda x: x[0], ids))

    # Закрываем соединение
    connection.close()

    return ids


# Получаем позицию меню по id
def get_menu_position_by_id(menu_id: int) -> MenuPosition | None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Получаем данные о позиции
    cursor.execute('SELECT name, price FROM menu WHERE id = ?', (menu_id,))
    result = cursor.fetchall()
    position = None
    if result:
        position = MenuPosition(id=menu_id, name=result[0][0], price=result[0][1])

    # Закрываем соединение
    connection.close()

    return position


# Создание записи нового заказа и получение id
def set_order(order: Order) -> int:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Добавление нового заказа
    cursor.execute('INSERT INTO "order" (time, price, positions) VALUES (?, ?, ?)',
                   (order.time, order.total_price, json.dumps(order.positions, cls=OrderEncoder)))

    # Сохраняем изменения
    connection.commit()

    # Получаем id заказа
    cursor.execute('SELECT id FROM "order" WHERE time = ? AND price = ?', (order.time, order.total_price))
    order_id = cursor.fetchall()[0][0]

    # Закрываем соединение
    connection.close()

    return order_id


# Записываем заказ пользователю
def set_order_id_to_user(email: str, order_id: int):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Записываем пользователю заказ
    cursor.execute('INSERT INTO user_orders (email, order_id) VALUES (?, ?)', (email, order_id))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


# Получаем заказ по id
def get_order_by_id(order_id: int) -> Order | None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Получаем данные о позиции
    cursor.execute('SELECT time, price, positions FROM "order" WHERE id = ?', (order_id,))
    result = cursor.fetchall()
    order = None
    if result:
        order = Order(id=order_id, time=datetime.strptime(result[0][0], '%Y-%m-%d %H:%M:%S.%f'),
                      total_price=result[0][1], positions=json.loads(result[0][2]))

    # Закрываем соединение
    connection.close()

    return order


# Получаем id заказов по email
def get_order_ids_by_email(email: str) -> list[int] | None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Получаем id заказов
    cursor.execute('SELECT order_id FROM user_orders WHERE email = ?', (email,))
    result = cursor.fetchall()
    ids = None
    if result:
        ids = list(map(lambda x: x[0], result))

    # Закрываем соединение
    connection.close()

    return ids
