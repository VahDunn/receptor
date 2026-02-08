from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    name: str
    type_code: str
    unit: str
    calories_per_unit: int
    price_rub: int

    class Config:
        from_attributes = True
