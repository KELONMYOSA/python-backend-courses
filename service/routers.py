import re
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from service.contracts import Token, UserReg, User
from service.utils.auth import create_access_token, verify_password, validate_access_token
from service.utils.dao import get_users_email, set_user, get_user_by_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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
async def register(user: UserReg):
    # Проверка валидности электронной почты
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Email validation error')

    # Проверка, что пользователь с указанной электронной почтой не существует
    if user.email in get_users_email():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='A user with this email already exists')

    # Проверка, что пароль содержит символы
    if not len(user.password) > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='The password cannot be empty')

    # Записываем пользователя в БД
    set_user(user)

    # Создание токена аутентификации
    access_token = create_access_token(user.email)

    # Возвращение токена аутентификации
    return {"access_token": access_token, "token_type": "bearer"}


# Аутентификация пользователя
@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Проверка электронной почты пользователя и получение хеша его пароля из базы данных
    user = get_user_by_email(form_data.username)
    if user.hashed_password is None:
        raise credentials_exception

    # Проверка соответствия пароля
    if not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception

    # Создание токена аутентификации
    access_token = create_access_token(form_data.username)

    return {"access_token": access_token, "token_type": "bearer"}


# Получение данных пользователя
@router.get("/me", response_model=User)
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Проверка валидности токена и получение email
    email = validate_access_token(token)

    # Получение данных пользователя
    user_db = get_user_by_email(email)
    if user_db is None:
        raise credentials_exception
    user = User(name=user_db.name, email=user_db.email)

    return user
