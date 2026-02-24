from fastapi import APIRouter, status

from receptor.api.schemas.menu import MenuCreateParams
from receptor.dependencies.deps import depends_menus_service
from receptor.services.menu_service import MenuService

router = APIRouter(tags=["menus"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_products(
    params: MenuCreateParams,
    service: MenuService = depends_menus_service,
):
    return await service.create_menu(params)
