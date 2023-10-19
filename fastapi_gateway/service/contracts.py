import datetime
import json

from pydantic import BaseModel


class User(BaseModel):
    name: str | None = None
    email: str


class UserReg(User):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class MenuPosition(BaseModel):
    id: int
    name: str
    price: float


class OrderForm(BaseModel):
    menu_position_id: int
    count: int


class OrderPosition(BaseModel):
    count: int
    menu_position: MenuPosition


class Order(BaseModel):
    id: int | None = None
    time: datetime.datetime
    total_price: float
    positions: list[OrderPosition]


class OrderEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, OrderPosition):
            return obj.__dict__
        if isinstance(obj, MenuPosition):
            return obj.__dict__
        if isinstance(obj, OrderForm):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)
