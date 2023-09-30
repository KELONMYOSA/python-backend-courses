import datetime
import sqlite3

from service.contracts import User, UserData
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
    emails = map(lambda x: x[0], emails)

    # Закрываем соединение
    connection.close()

    return emails


# Создание нового пользователя
def set_user(user: User):
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


# Получение хеша пароля
def get_hashed_password(email: str) -> str | None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Получаем хеш
    cursor.execute('SELECT password FROM user WHERE email = ?', (email,))
    result = cursor.fetchall()
    pass_hash = None
    if result:
        pass_hash = result[0][0]

    # Закрываем соединение
    connection.close()

    return pass_hash


# Обновление токена
def update_token(email: str, token: str):
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Обновляем токен
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
    cursor.execute("INSERT INTO token (email, token, expires) VALUES (?, ?, ?) "
                   "ON CONFLICT (email) DO UPDATE SET token = ?, expires = ? "
                   "WHERE email = ?", (email, token, expiration_time, token, expiration_time, email))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


# Получаем данные пользователя по email
def get_user_by_email(email: str) -> UserData | None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Получаем данные пользователя
    cursor.execute('SELECT name, email FROM user WHERE email = ?', (email,))
    result = cursor.fetchall()
    user = None
    if result:
        user = UserData(name=result[0][0], email=result[0][1])

    # Закрываем соединение
    connection.close()

    return user


# Получаем email пользователя по токену
def get_email_by_token(token: str) -> str | None:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Получаем данные пользователя
    cursor.execute('SELECT email, expires FROM token WHERE token = ?', (token,))
    result = cursor.fetchall()
    email = None
    expiration_time = None
    if result:
        email = result[0][0]
        expiration_time = result[0][1]

    # Проверяем действительность токена
    if expiration_time is not None:
        expiration_time = datetime.datetime.strptime(expiration_time, "%Y-%m-%d %H:%M:%S.%f")
        if expiration_time < datetime.datetime.now():
            email = None

    # Закрываем соединение
    connection.close()

    return email


# Получаем данные пользователя по токену
def get_user_by_token(token: str) -> UserData | None:
    # Получаем email по токену
    email = get_email_by_token(token)
    if email is None:
        return None

    # Получаем данные пользователя по email
    user = get_user_by_email(email)

    return user
