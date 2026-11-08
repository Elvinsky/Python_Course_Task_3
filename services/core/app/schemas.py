from pydantic import BaseModel, ConfigDict, Field


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    stock: int


class PriceUpdate(BaseModel):
    price: float = Field(gt=0)


class StockUpdate(BaseModel):
    stock: int = Field(ge=0)


class OrderIn(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    item_id: int
    quantity: int
