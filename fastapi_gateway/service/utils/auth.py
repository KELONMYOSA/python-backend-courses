from datetime import datetime, timedelta

from grpc import aio
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext

from config import settings
from service.contracts import User, UserReg
from service.utils.dao import Database
from pb_auth import auth_pb2
from pb_auth.auth_pb2_grpc import AuthServiceStub

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Сравнение пароля и хэша
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, str.encode(hashed_password))


# Создание хэшированного пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Создание токена
def create_access_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email,
               "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Проверка корректности данных и создание пользователя
async def create_new_user(user: UserReg) -> dict:
    async with aio.insecure_channel(settings.GO_AUTH_SERVER) as channel:
        stub = AuthServiceStub(channel)
        try:
            response = await stub.CreateNewUser(auth_pb2.UserReg(name=user.name, email=user.email,
                                                                 password=user.password))
        except aio.AioRpcError as rpc_error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=rpc_error.details())

    return {"access_token": response.access_token, "token_type": response.token_type}


# Проверка корректности данных и получение токена
def login_user(form_data: OAuth2PasswordRequestForm) -> dict:
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


# Проверка токена и получение данных пользователя
def authorize_user(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Получение данных пользователя
    with Database() as db:
        user_db = db.get_user_by_email(email)
    if user_db is None:
        raise credentials_exception
    user = User(name=user_db.name, email=user_db.email)

    return user
