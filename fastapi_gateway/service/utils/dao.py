import json
import sqlite3
from datetime import datetime

from config import settings
from service.contracts import UserReg, UserInDB, MenuPosition, Order, OrderEncoder


class Database:
    __DB_PATH = settings.DB_PATH

    # Устанавливаем соединение с базой данных
    def __init__(self, db_location: str = None):
        if db_location is not None:
            self.connection = sqlite3.connect(db_location)
        else:
            self.connection = sqlite3.connect(self.__DB_PATH)
        self.cur = self.connection.cursor()

    def __enter__(self):
        return self

    # Сохраняем изменения и закрываем соединение
    def __exit__(self, ext_type, exc_value, traceback):
        self.cur.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

    # Получение всех email пользователей
    def get_users_email(self) -> list[str]:
        self.cur.execute('SELECT email FROM user')
        emails = self.cur.fetchall()
        emails = list(map(lambda x: x[0], emails))

        return emails

    # Создание нового пользователя
    def set_user(self, user: UserReg, hashed_password: str):
        self.cur.execute('INSERT INTO user (name, email, password) VALUES (?, ?, ?)',
                         (user.name, user.email, hashed_password))

    # Получаем данные пользователя по email
    def get_user_by_email(self, email: str) -> UserInDB | None:
        self.cur.execute('SELECT name, email, password FROM user WHERE email = ?', (email,))
        result = self.cur.fetchall()
        user = None
        if result:
            user = UserInDB(name=result[0][0], email=result[0][1], hashed_password=result[0][2])

        return user

    # Получение всех id позиций в меню
    def get_menu_ids(self) -> list[int]:
        self.cur.execute('SELECT id FROM menu')
        ids = self.cur.fetchall()
        ids = list(map(lambda x: x[0], ids))

        return ids

    # Получаем позицию меню по id
    def get_menu_position_by_id(self, menu_id: int) -> MenuPosition | None:
        self.cur.execute('SELECT name, price FROM menu WHERE id = ?', (menu_id,))
        result = self.cur.fetchall()
        position = None
        if result:
            position = MenuPosition(id=menu_id, name=result[0][0], price=result[0][1])

        return position

    # Создание записи нового заказа и получение id
    def set_order(self, order: Order) -> int:
        # Добавление нового заказа
        self.cur.execute('INSERT INTO "order" (time, price, positions) VALUES (?, ?, ?)',
                         (order.time, order.total_price, json.dumps(order.positions, cls=OrderEncoder)))

        # Сохраняем изменения
        self.connection.commit()

        # Получаем id заказа
        self.cur.execute('SELECT id FROM "order" WHERE time = ? AND price = ?', (order.time, order.total_price))
        order_id = self.cur.fetchall()[0][0]

        return order_id

    # Записываем заказ пользователю
    def set_order_id_to_user(self, email: str, order_id: int):
        self.cur.execute('INSERT INTO user_orders (email, order_id) VALUES (?, ?)', (email, order_id))

    # Получаем заказ по id
    def get_order_by_id(self, order_id: int) -> Order | None:
        self.cur.execute('SELECT time, price, positions FROM "order" WHERE id = ?', (order_id,))
        result = self.cur.fetchall()
        order = None
        if result:
            order = Order(id=order_id, time=datetime.strptime(result[0][0], '%Y-%m-%d %H:%M:%S.%f'),
                          total_price=result[0][1], positions=json.loads(result[0][2]))

        return order

    # Получаем id заказов по email
    def get_order_ids_by_email(self, email: str) -> list[int] | None:
        self.cur.execute('SELECT order_id FROM user_orders WHERE email = ?', (email,))
        result = self.cur.fetchall()
        ids = None
        if result:
            ids = list(map(lambda x: x[0], result))

        return ids
