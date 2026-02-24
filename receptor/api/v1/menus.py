from fastapi import APIRouter, status, Depends

from receptor.api.schemas.menu import MenuCreateParams
from receptor.api.deps.services import get_menu_service
from receptor.services.menu_service import MenuService

router = APIRouter(tags=["menus"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_menu(
    params: MenuCreateParams,
    service: MenuService = Depends(get_menu_service),
):
    return await service.create_menu(params)
