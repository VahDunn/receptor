from pydantic import BaseModel

from receptor.core.domain.marketplaces import Marketplace


class ProductOut(BaseModel):
    id: int
    name: str
    type_code: str
    unit: str
    calories_per_unit: int
    price_rub: int
    marketplace: str

    class Config:
        from_attributes = True

class ProductCreateParams(BaseModel):
    marketplace: Marketplace = Marketplace.perekrestok
