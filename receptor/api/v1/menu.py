from fastapi import APIRouter, status
from fastapi.params import Depends

from receptor.api.deps import crud_service_dep

router = APIRouter(tags=['users'])

MenuServiceDep = Depends(crud_service_dep(MenuService, MenuRepository))


@router.post('', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_menu(
    payload: MenuCreate,
    service: MenuService = MenuServiceDep,
) -> UserOut:
    return await service.create(payload)
