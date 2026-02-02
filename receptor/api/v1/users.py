from fastapi import APIRouter, status
from fastapi.params import Depends

from receptor.api.deps import crud_service_dep
from receptor.api.schemas.user import UserCreate, UserOut
from receptor.repositories.user import UserRepository
from receptor.services.user import UserService

router = APIRouter(tags=['users'])

UserServiceDep = Depends(crud_service_dep(UserService, UserRepository))


@router.post('', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserService = UserServiceDep,
) -> UserOut:
    return await service.create(payload)
