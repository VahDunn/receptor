from fastapi import APIRouter, Depends, status

from receptor.api.deps.services import get_menu_service
from receptor.schemas.menu import MenuCreateParams, MenuOut
from receptor.services.menu_service import MenuService

router = APIRouter(tags=["menus"])

menu_service = Depends(get_menu_service)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=MenuOut)
async def create_menu(
    params: MenuCreateParams,
    service: MenuService = menu_service,
):
    return await service.create(params)


@router.get("/user/{user_id}", response_model=list[MenuOut])
async def get_menus_by_user(
    user_id: int,
    service: MenuService = menu_service,
):
    return await service.get(user_id)
