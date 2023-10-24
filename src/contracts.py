from pydantic import BaseModel


class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float
