from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.api.deps.db import get_db
from receptor.repositories.menu_repo import MenuRepository
from receptor.repositories.payment_repo import PaymentRepository
from receptor.repositories.product_repo import ProductRepository


def get_product_repository(
    db: AsyncSession = Depends(get_db),
) -> ProductRepository:
    return ProductRepository(db=db)


def get_menu_repository(
    db: AsyncSession = Depends(get_db),
) -> MenuRepository:
    return MenuRepository(db=db)

def get_payment_repository(
    db: AsyncSession = Depends(get_db),
) -> PaymentRepository:
    return PaymentRepository(db=db)
