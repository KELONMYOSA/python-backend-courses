from pydantic import BaseModel


class User(BaseModel):
    name: str | None = None
    email: str


class UserReg(User):
    password: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str
