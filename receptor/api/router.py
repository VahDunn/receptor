from fastapi import APIRouter

from receptor.api.deps import depends_ai
from receptor.api.v1.users import router as users_router
from receptor.external_services.ai.abstract_ai_client import AbstractAIClient

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["users"])


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}


@api_router.get("/ai_health")
async def ai_health_check(
    ai: AbstractAIClient = depends_ai,
):
    res = await ai.send_prompt("ping")
    return {
        "status": res,
    }
