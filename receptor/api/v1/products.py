from fastapi import APIRouter, status, Depends, Query

from receptor.api.schemas.product import ProductOut, ProductCreateParams
from receptor.api.deps.services import get_products_service
from receptor.services.product_service import ProductsService

router = APIRouter()


@router.post(
    "",
    response_model=list[ProductOut],
    status_code=status.HTTP_201_CREATED,
)
async def create_products(
    params: ProductCreateParams,
    service: ProductsService = Depends(get_products_service),
):
    return await service.create_products_pool(marketplace=params.marketplace)
