from fastapi import APIRouter, status

from receptor.api.schemas.product import ProductOut
from receptor.dependencies.deps import depends_products_service
from receptor.services.product import ProductsService

router = APIRouter(tags=["products"])


@router.post("", response_model=list[ProductOut], status_code=status.HTTP_201_CREATED)
async def create_products(
    service: ProductsService = depends_products_service,
):
    return await service.create_products()
