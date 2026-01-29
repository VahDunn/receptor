from contextlib import asynccontextmanager

from fastapi import FastAPI

from receptor.api.router import api_router
from receptor.db.engine import engine
from receptor.api.error_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app_main: FastAPI):
    # startup
    yield
    # shutdown
    await engine.dispose()


def create_app() -> FastAPI:
    main_app = FastAPI(
        title='Receptor API',
        version='1.0.0',
        lifespan=lifespan,
    )
    register_exception_handlers(main_app)
    main_app.include_router(api_router, prefix='/api/v1')

    return main_app


app = create_app()
