import sqlite3

from service.contracts import UserReg, UserInDB
from service.utils.auth import get_password_hash

DB_PATH = "service/database.sqlite"


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
def set_user(user: UserReg):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Хеширование пароля
    hashed_password = get_password_hash(user.password)

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
