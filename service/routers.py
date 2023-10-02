import re
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from service.contracts import Token, UserReg, User, Order, OrderForm
from service.utils.auth import create_access_token, verify_password, authorize_user, get_password_hash
from service.utils.dao import Database
from service.utils.orders import check_order_form, create_order, get_orders_by_email, get_order_by_id_and_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Приветственная HTML страница
@router.get("/", tags=["HTML"])
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
@router.post("/register", response_model=Token, tags=["Authorization"])
async def register(user: UserReg):
    # Проверка валидности электронной почты
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Email validation error')

    # Проверка, что пользователь с указанной электронной почтой не существует
    with Database() as db:
        if user.email in db.get_users_email():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='A user with this email already exists')

    # Проверка, что пароль содержит символы
    if not len(user.password) > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='The password cannot be empty')

    # Хеширование пароля
    hashed_password = get_password_hash(user.password)

    # Записываем пользователя в БД
    with Database() as db:
        db.set_user(user, hashed_password)

    # Создание токена аутентификации
    access_token = create_access_token(user.email)

    return {"access_token": access_token, "token_type": "bearer"}


# Аутентификация пользователя
@router.post("/login", response_model=Token, tags=["Authorization"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Проверка электронной почты пользователя и получение хеша его пароля из базы данных
    with Database() as db:
        user = db.get_user_by_email(form_data.username)
    if user is None:
        raise credentials_exception

    # Проверка соответствия пароля
    if not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception

    # Создание токена аутентификации
    access_token = create_access_token(form_data.username)

    return {"access_token": access_token, "token_type": "bearer"}


# Получение данных пользователя
@router.get("/me", response_model=User, tags=["Authorization"])
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    return authorize_user(token)


# Создание заказа
@router.post("/order", response_model=Order, tags=["Orders"])
def set_user_order(order_form: list[OrderForm], token: Annotated[str, Depends(oauth2_scheme)]):
    # Авторизация пользователя
    user = authorize_user(token)

    # Проверка состава заказа
    if not check_order_form(order_form):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='The items specified in the order were not found')

    # Создание заказа пользователя
    order = create_order(order_form, user.email)

    return order


# Получение заказов пользователя
@router.get("/orders", response_model=list[Order], tags=["Orders"])
def get_user_orders(token: Annotated[str, Depends(oauth2_scheme)]):
    # Авторизация пользователя
    user = authorize_user(token)

    # Получение заказов пользователя
    orders = get_orders_by_email(user.email)

    return orders


# Получение заказа пользователя по id
@router.get("/order/{order_id}", response_model=Order, tags=["Orders"])
def get_user_order_by_id(order_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    # Авторизация пользователя
    user = authorize_user(token)

    # Получение заказа пользователя
    order = get_order_by_id_and_email(user.email, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='An order with this id was not found for this user')

    return order
