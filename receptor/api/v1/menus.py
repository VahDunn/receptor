from fastapi import APIRouter, status, Depends, HTTPException

from receptor.api.schemas.menu import MenuCreateParams, MenuResponseSchema
from receptor.api.deps.services import get_menu_service
from receptor.services.menu_service import MenuService

router = APIRouter(tags=["menus"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=MenuResponseSchema)
async def create_menu(
    params: MenuCreateParams,
    service: MenuService = Depends(get_menu_service),
):
    return await service.create(params)


@router.get("/user/{user_id}", response_model=MenuResponseSchema)
async def get_menu_by_user(
    user_id: int,
    service: MenuService = Depends(get_menu_service),
):
    menu = await service.get(user_id)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found",
        )
    return menu
