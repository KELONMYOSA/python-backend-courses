import re

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import HTMLResponse

from service.contracts import Token, User, LoginData, UserData
from service.utils.auth import create_access_token, verify_password
from service.utils.dao import get_users_email, set_user, get_hashed_password, update_token, get_user_by_token

router = APIRouter()


# Приветственная HTML страница
@router.get("/", tags=["html"])
def root():
    html_content = '''
    <html>
        <body>
            <h1>Homework for the ITMO course Python Backend</h1>
        </body>
    </html>
    '''
    return HTMLResponse(content=html_content, status_code=200)


# Регистрация нового пользователя
@router.post("/register", response_model=Token)
async def register(user: User):
    # Проверка валидности электронной почты
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user.email):
        raise HTTPException(status_code=403, detail='Email validation error')

    # Проверка, что пользователь с указанной электронной почтой не существует
    if user.email in get_users_email():
        raise HTTPException(status_code=403, detail='A user with this email already exists')

    # Записываем пользователя в БД
    set_user(user)

    # Создание токена аутентификации
    access_token = create_access_token(user.email)
    update_token(user.email, access_token)

    # Возвращение токена аутентификации
    return {"access_token": access_token, "token_type": "bearer"}


# Аутентификация пользователя
@router.post("/login", response_model=Token)
async def login(user: LoginData):
    # Проверка электронной почты пользователя и получение хеша его пароля из базы данных
    email_hashed_password = get_hashed_password(user.email)
    if email_hashed_password is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Проверка соответствия пароля
    if not verify_password(user.password, email_hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Создание токена аутентификации
    access_token = create_access_token(user.email)
    update_token(user.email, access_token)

    return {"access_token": access_token, "token_type": "bearer"}


# Получение данных пользователя
@router.get("/me", response_model=UserData)
def get_current_user(token: str = Header(...)):
    # Проверка валидности токена и получение данных пользователя
    user = get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect token")

    return user
