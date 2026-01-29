from fastapi import APIRouter

from receptor.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(users_router, prefix='/users', tags=['users'])


@api_router.get('/health')
async def health_check():
    return {'status': 'ok'}
