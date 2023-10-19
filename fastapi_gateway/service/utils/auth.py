from grpc import aio
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from config import settings
from service.contracts import User, UserReg
from pb_auth import auth_pb2
from pb_auth.auth_pb2_grpc import AuthServiceStub


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
async def login_user(form_data: OAuth2PasswordRequestForm) -> dict:
    async with aio.insecure_channel(settings.GO_AUTH_SERVER) as channel:
        stub = AuthServiceStub(channel)
        try:
            response = await stub.LoginUser(auth_pb2.UserLogin(email=form_data.username, password=form_data.password))
        except aio.AioRpcError as rpc_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=rpc_error.details(),
                headers={"WWW-Authenticate": "Bearer"},
            )

    return {"access_token": response.access_token, "token_type": response.token_type}


# Проверка токена и получение данных пользователя
async def authorize_user(token: str) -> User:
    async with aio.insecure_channel(settings.GO_AUTH_SERVER) as channel:
        stub = AuthServiceStub(channel)
        try:
            response = await stub.AuthUser(auth_pb2.Token(access_token=token, token_type="bearer"))
        except aio.AioRpcError as rpc_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=rpc_error.details(),
                headers={"WWW-Authenticate": "Bearer"},
            )

    return User(name=response.name, email=response.email)
