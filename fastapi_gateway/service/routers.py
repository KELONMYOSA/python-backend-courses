import io
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from service.contracts import Token, UserReg, User, Order, OrderForm
from service.utils.auth import create_new_user, login_user, authorize_user
from service.utils.orders import check_order_form, create_order, get_orders_by_email, get_order_by_id_and_email, \
    get_user_dishes_chart_png

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
    return await create_new_user(user)


# Аутентификация пользователя
@router.post("/login", response_model=Token, tags=["Authorization"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await login_user(form_data)


# Получение данных пользователя
@router.get("/me", response_model=User, tags=["Authorization"])
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    return await authorize_user(token)


# Создание заказа
@router.post("/order", response_model=Order, tags=["Orders"])
async def set_user_order(order_form: list[OrderForm], token: Annotated[str, Depends(oauth2_scheme)]):
    # Авторизация пользователя
    user = await authorize_user(token)

    # Проверка состава заказа
    if not check_order_form(order_form):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='The items specified in the order were not found')

    # Создание заказа пользователя
    order = create_order(order_form, user.email)

    return order


# Получение заказов пользователя
@router.get("/orders", response_model=list[Order], tags=["Orders"])
async def get_user_orders(token: Annotated[str, Depends(oauth2_scheme)]):
    # Авторизация пользователя
    user = await authorize_user(token)

    # Получение заказов пользователя
    orders = get_orders_by_email(user.email)

    return orders


# Получение png с круговой диаграммой количества блюд в заказах
@router.get("/orders/chart/dishes", tags=["Orders"])
async def get_user_dishes_chart(token: Annotated[str, Depends(oauth2_scheme)]):
    # Авторизация пользователя
    user = await authorize_user(token)

    # Получение заказов пользователя
    orders = get_orders_by_email(user.email)

    # Получаем картинку
    img_bytes = await get_user_dishes_chart_png(user.email, orders)

    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")


# Получение заказа пользователя по id
@router.get("/order/{order_id}", response_model=Order, tags=["Orders"])
async def get_user_order_by_id(order_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    # Авторизация пользователя
    user = await authorize_user(token)

    # Получение заказа пользователя
    order = get_order_by_id_and_email(user.email, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='An order with this id was not found for this user')

    return order
