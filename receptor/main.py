from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI

from receptor.api.router import api_router
from receptor.config import settings
from receptor.core.logger import setup_logging
from receptor.db.admin import setup_admin
from receptor.db.engine import engine
from receptor.api.error_handlers import register_exception_handlers
from receptor.external_services.ai.clients.chad_ai_client import ChadAIClient


@asynccontextmanager
async def lifespan(app_main: FastAPI):
    # startup
    setup_logging(app_name="receptor")
    app_main.state.http_session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(
            total=12000,  # общий потолок
            connect=1000,  # соединение
            sock_connect=1000,  # коннект до сокета
            sock_read=1100,
        )
    )
    app_main.state.ai_client = ChadAIClient(
        session=app_main.state.http_session,
        api_key=settings.chad_api_key,
        url=settings.chad_url,
    )
    yield
    # shutdown
    await app_main.state.http_session.close()
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
