from pydantic import BaseModel


class User(BaseModel):
    name: str | None
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class UserData(BaseModel):
    name: str | None
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str
