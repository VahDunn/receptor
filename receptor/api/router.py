from fastapi import APIRouter, Depends

from receptor.dependencies.deps import get_ai_client
from receptor.api.v1.products import router as products_router

depends_ai = Depends(get_ai_client)

api_router = APIRouter()
api_router.include_router(products_router, prefix="/products", tags=["products"])


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}


@api_router.get("/ai_health")
async def ai_health_check(
    ai=depends_ai,
):
    res = await ai.send_prompt("ping")
    return {
        "status": res,
    }
