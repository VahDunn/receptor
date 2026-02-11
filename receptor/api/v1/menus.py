from fastapi import APIRouter, status

from receptor.dependencies.deps import depends_menus_service
from receptor.services.menu import MenuService

router = APIRouter(tags=["menus"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_products(
    service: MenuService = depends_menus_service,
):
    return await service.create_menu()
