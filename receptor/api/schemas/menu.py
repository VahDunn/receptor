from pydantic import BaseModel, Field


class MenuCreateParams(BaseModel):
    user_id: int
    max_kcal: int
    min_kcal: int
    max_money: int = 10000
    excluded_products_ids: list[int] = Field(default_factory=list)
