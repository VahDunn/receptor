from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from receptor.api.error_handlers import register_exception_handlers
from receptor.api.router import api_router
from receptor.core.logger import setup_logging
from receptor.db.admin import setup_admin
from receptor.db.engine import engine


@asynccontextmanager
async def lifespan(app_main: FastAPI):
    setup_logging(app_name="receptor")

    app_main.state.ai_http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            timeout=1200.0,
            connect=10.0,
            read=1100.0,
            write=30.0,
            pool=30.0,
        )
    )

    app_main.state.payments_http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            timeout=20.0,
            connect=5.0,
            read=15.0,
            write=10.0,
            pool=5.0,
        )
    )

    yield

    await app_main.state.ai_http_client.aclose()
    await app_main.state.payments_http_client.aclose()
    await engine.dispose()


def create_app() -> FastAPI:
    main_app = FastAPI(
        title="Receptor API",
        version="0.0.1",
        lifespan=lifespan,
    )
    setup_admin(main_app)
    register_exception_handlers(main_app)
    main_app.include_router(api_router, prefix="/api")
    return main_app


app = create_app()