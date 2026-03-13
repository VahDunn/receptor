from receptor.core.domain.marketplaces import Marketplace
from receptor.core.domain.product_categories import ProductTypeCode
from receptor.core.errors import EntityNotFoundError
from receptor.db.models import Product
from receptor.repositories.product_repo import ProductRepository
from receptor.repositories.user_excluded_product_repo import (
    UserExcludedProductsRepository,
)
from receptor.repositories.user_repo import UserRepository
from receptor.services.dto.product import ProductFilterDTO


class UserExcludedProductsService:
    def __init__(
        self,
        repo: UserExcludedProductsRepository,
        user_repo: UserRepository,
        product_repo: ProductRepository,
    ) -> None:
        self._repo = repo
        self._user_repo = user_repo
        self._product_repo = product_repo

    async def get_excluded_products(
        self,
        *,
        user_id: int,
    ) -> list[Product]:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")

        return await self._repo.get_excluded_products(user_id=user_id)

    async def add_excluded_product(
        self,
        *,
        user_id: int,
        product_id: int,
    ) -> list[int]:
        try:
            user = await self._user_repo.get_by_id(user_id)
            if not user:
                raise EntityNotFoundError(f"User {user_id} not found")

            product = await self._product_repo.get_by_id(product_id)
            if not product:
                raise EntityNotFoundError(f"Product {product_id} not found")

            result = await self._repo.exclude_products(
                user_id=user_id,
                product_ids=[product_id],
            )
            await self._repo.db.commit()
            return result
        except Exception:
            await self._repo.db.rollback()
            raise

    async def remove_excluded_product(
        self,
        *,
        user_id: int,
        product_id: int,
    ) -> list[int]:
        try:
            user = await self._user_repo.get_by_id(user_id)
            if not user:
                raise EntityNotFoundError(f"User {user_id} not found")

            result = await self._repo.remove_excluded_products(
                user_id=user_id,
                product_ids=[product_id],
            )
            await self._repo.db.commit()
            return result
        except Exception:
            await self._repo.db.rollback()
            raise

    async def add_excluded_products_by_category(
        self,
        *,
        user_id: int,
        category: ProductTypeCode,
        marketplace: Marketplace,
    ) -> list[int]:
        try:
            user = await self._user_repo.get_by_id(user_id)
            if not user:
                raise EntityNotFoundError(f"User {user_id} not found")

            products = await self._product_repo.get(
                filters=ProductFilterDTO(
                    category=category,
                    marketplace=marketplace,
                    limit=10_000,
                )
            )
            product_ids = [product.id for product in products]

            result = await self._repo.exclude_products(
                user_id=user_id,
                product_ids=product_ids,
            )
            await self._repo.db.commit()
            return result
        except Exception:
            await self._repo.db.rollback()
            raise

    async def remove_excluded_products_by_category(
        self,
        *,
        user_id: int,
        category: ProductTypeCode,
        marketplace: Marketplace,
    ) -> list[int]:
        try:
            user = await self._user_repo.get_by_id(user_id)
            if not user:
                raise EntityNotFoundError(f"User {user_id} not found")

            products = await self._product_repo.get(
                filters=ProductFilterDTO(
                    category=category,
                    marketplace=marketplace,
                    limit=10_000,
                )
            )

            product_ids = [p.id for p in products]

            result = await self._repo.remove_excluded_products(
                user_id=user_id,
                product_ids=product_ids,
            )

            await self._repo.db.commit()
            return result

        except Exception:
            await self._repo.db.rollback()
            raise
