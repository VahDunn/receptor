from fastapi import APIRouter, status, Depends

from receptor.api.schemas.product import ProductOut
from receptor.api.deps.services import get_products_service
from receptor.services.product_service import ProductsService

router = APIRouter()


@router.post(
    "",
    response_model=list[ProductOut],
    status_code=status.HTTP_201_CREATED,
)
async def create_products(
    service: ProductsService = Depends(get_products_service),
):
    return await service.create_products_pool()
