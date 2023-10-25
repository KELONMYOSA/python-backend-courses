from pydantic import BaseModel, RootModel


class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float


class OrderItems(RootModel):
    root: list[OrderItem]
