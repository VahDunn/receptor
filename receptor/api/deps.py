from functools import lru_cache
from typing import AsyncGenerator, TypeVar, Callable, Type, Awaitable

from fastapi import Depends, Header, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from receptor.config import get_settings
from receptor.db.engine import AsyncSessionLocal
from receptor.external_services.ai.abstract_ai_client import AbstractAIClient
from receptor.external_services.ai.chad_ai_client import ChadAIClient
from receptor.repositories.base_crud import BaseCrudRepository
from receptor.services.abstract_crud import AbstractCrudService

TRepo = TypeVar("TRepo", bound=BaseCrudRepository)
TService = TypeVar("TService", bound=AbstractCrudService)
x_user_header = Header(default=None, alias="X-User-Id")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@lru_cache(maxsize=1)
async def get_ai_client(request: Request) -> AbstractAIClient:
    session = request.app.state.http_session
    settings = get_settings()
    api_key = settings.chad_api_key
    url = settings.chad_url
    return ChadAIClient(session=session, api_key=api_key, url=url)


depends_ai = Depends(get_ai_client)
depends_db = Depends(get_db)


async def get_current_user_id(
    x_user_id: int | None = x_user_header,
) -> int:
    if x_user_id is None:
        return 1
    if x_user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Id must be positive integer",
        )
    return x_user_id


depends_user_id = Depends(get_current_user_id)


def crud_service_dep(
    service_cls: Type[TService],
    repo_cls: Type[TRepo],
) -> Callable[..., Awaitable[TService]]:
    async def _dep(
        db: AsyncSession = depends_db,
        user_id: int = depends_user_id,
    ) -> TService:
        repo = repo_cls(db)
        return service_cls(repo=repo, user_id=user_id)

    return _dep
