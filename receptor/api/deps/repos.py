from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.api.deps.db import get_db
from receptor.repositories import UserRepository, ProductRepository, MenuRepository, PaymentRepository


def get_user_repo(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(db)

def get_product_repo(
    db: AsyncSession = Depends(get_db),
) -> ProductRepository:
    return ProductRepository(db=db)


def get_menu_repo(
    db: AsyncSession = Depends(get_db),
) -> MenuRepository:
    return MenuRepository(db=db)

def get_payment_repo(
    db: AsyncSession = Depends(get_db),
) -> PaymentRepository:
    return PaymentRepository(db=db)
