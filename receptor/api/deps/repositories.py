from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.deps.db import get_db
from receptor.repositories.product_repo import ProductRepository


def get_product_repository(
    db: AsyncSession = Depends(get_db),
) -> ProductRepository:
    return ProductRepository(db=db)
